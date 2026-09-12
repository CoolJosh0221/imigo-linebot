"""Pytest configuration and fixtures"""

import pytest
from pathlib import Path


@pytest.fixture
def test_env(monkeypatch):
    """Set up test environment variables"""
    monkeypatch.setattr("config.load_dotenv", lambda: None)
    for key, value in {
        "LINE_CHANNEL_SECRET": "test-secret",
        "LINE_CHANNEL_ACCESS_TOKEN": "test-token",
        "LLM_BASE_URL": "http://localhost:8001/v1",
        "MODEL_NAME": "test-model",
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "DEFAULT_LANGUAGE": "id",
        "LLM_API_KEY": "test-key",
        "LLM_CHAT_TEMPLATE_KWARGS": "{}",
        "CHAT_HISTORY_MESSAGES": "12",
        "CHAT_INPUT_MAX_BYTES": "6000",
        "LLM_TIMEOUT_SECONDS": "20",
    }.items():
        monkeypatch.setenv(key, value)
    yield


@pytest.fixture
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent
