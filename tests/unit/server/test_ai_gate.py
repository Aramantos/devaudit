"""
Tests for the AI feature gate - AI is OFF by default (decision 2026-07-04).
"""
import asyncio

import pytest

fastapi = pytest.importorskip("fastapi", reason="server extra not installed")

import importlib

# devaudit.server's __init__ re-exports the FastAPI instance as `app`, which
# shadows the app *module* on attribute access - import the module explicitly.
app_module = importlib.import_module("devaudit.server.app")


@pytest.fixture
def ai_off(monkeypatch):
    monkeypatch.delenv("DEVAUDIT_ENABLE_AI", raising=False)


@pytest.fixture
def ai_on(monkeypatch):
    monkeypatch.setenv("DEVAUDIT_ENABLE_AI", "1")


def test_ai_disabled_by_default(ai_off):
    assert app_module.ai_features_enabled() is False


def test_ai_enabled_by_env(ai_on):
    assert app_module.ai_features_enabled() is True


def test_ai_status_reports_disabled(ai_off):
    """/api/ai/status tells the dashboard AI is off, so the UI hides it."""
    status = asyncio.run(app_module.ai_status())
    assert status["available"] is False
    assert "disabled" in status["message"].lower() or "DEVAUDIT_ENABLE_AI" in status["message"]


def test_ai_analyze_refuses_when_disabled(ai_off):
    """/api/ai/analyze returns 503 with an actionable message when off."""
    response = asyncio.run(app_module.analyze_with_ai({"scan_results": {}}))
    assert response.status_code == 503


def test_ai_chat_refuses_when_disabled(ai_off):
    """/api/ai/chat returns 503 with an actionable message when off."""
    response = asyncio.run(app_module.chat_with_ai({"message": "hello"}))
    assert response.status_code == 503


def test_dashboard_dir_resolves_to_existing_convention():
    """The resolver prefers the package-internal copy and always returns a
    dashboard/dist-shaped path (wheel layout or source checkout layout)."""
    resolved = app_module._resolve_dashboard_dir()
    assert resolved.name == "dist"
    assert resolved.parent.name == "dashboard"
