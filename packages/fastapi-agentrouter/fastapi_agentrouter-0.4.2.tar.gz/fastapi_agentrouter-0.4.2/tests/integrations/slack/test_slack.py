"""Tests for Slack integration."""

from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent, router
from fastapi_agentrouter.core.settings import Settings, SlackSettings, get_settings


def test_slack_disabled():
    """Test Slack endpoint when disabled."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    # Create app with disabled Slack
    app = FastAPI()
    app.dependency_overrides[get_agent] = get_mock_agent
    app.dependency_overrides[get_settings] = lambda: Settings(slack=None)
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/agent/slack/events",
        json={"type": "url_verification", "challenge": "test"},
    )
    assert response.status_code == 404
    assert "Slack integration is not enabled" in response.json()["detail"]


def test_slack_events_missing_settings():
    """Test Slack events endpoint without Slack settings configured."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent] = get_mock_agent
    # Slack is disabled when slack=None
    app.dependency_overrides[get_settings] = lambda: Settings(slack=None)
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/agent/slack/events",
        json={"type": "url_verification", "challenge": "test_challenge"},
    )
    # Should return 404 because Slack is not enabled (slack=None means disabled)
    assert response.status_code == 404
    assert "Slack integration is not enabled" in response.json()["detail"]


def test_slack_events_endpoint():
    """Test the Slack events endpoint with mocked dependencies."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent] = get_mock_agent
    app.dependency_overrides[get_settings] = lambda: Settings(
        slack=SlackSettings(bot_token="test-token", signing_secret="test-secret")
    )
    app.include_router(router)
    client = TestClient(app)

    with (
        patch("slack_bolt.adapter.fastapi.SlackRequestHandler") as mock_handler_class,
        patch("slack_bolt.App") as mock_app_class,
        patch.dict(
            "os.environ",
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token",
                "SLACK_SIGNING_SECRET": "test-signing-secret",
            },
        ),
    ):
        # Mock the handler
        mock_handler = Mock()
        mock_handler.handle = AsyncMock(return_value={"ok": True})
        mock_handler_class.return_value = mock_handler

        # Mock the Slack app
        mock_app = Mock()
        mock_app_class.return_value = mock_app

        response = client.post(
            "/agent/slack/events",
            json={
                "type": "event_callback",
                "event": {
                    "type": "app_mention",
                    "text": "Hello bot!",
                    "user": "U123456",
                },
            },
        )
        assert response.status_code == 200


def test_slack_missing_library():
    """Test error when slack-bolt is not installed."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent] = get_mock_agent
    app.dependency_overrides[get_settings] = lambda: Settings(
        slack=SlackSettings(bot_token="test-token", signing_secret="test-secret")
    )
    app.include_router(router)
    client = TestClient(app)

    # Mock the import to fail when trying to import slack_bolt
    import builtins

    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "slack_bolt" or name.startswith("slack_bolt."):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    with (
        patch("builtins.__import__", side_effect=mock_import),
        patch.dict(
            "os.environ",
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token",
                "SLACK_SIGNING_SECRET": "test-signing-secret",
            },
        ),
    ):
        response = client.post(
            "/agent/slack/events",
            json={"type": "url_verification", "challenge": "test"},
        )
        assert response.status_code == 500
        assert "slack-bolt is required" in response.json()["detail"]
