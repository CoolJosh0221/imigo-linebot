"""Pytest configuration and fixtures"""
import pytest
import os
from pathlib import Path


@pytest.fixture
def test_env():
    """Set up test environment variables"""
    os.environ["LINE_CHANNEL_SECRET"] = "test-secret"
    os.environ["LINE_CHANNEL_ACCESS_TOKEN"] = "test-token"
    os.environ["LLM_BASE_URL"] = "http://localhost:8001/v1"
    os.environ["MODEL_NAME"] = "test-model"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["DEFAULT_LANGUAGE"] = "id"
    yield
    # Cleanup
    for key in [
        "LINE_CHANNEL_SECRET",
        "LINE_CHANNEL_ACCESS_TOKEN",
        "LLM_BASE_URL",
        "MODEL_NAME",
        "DATABASE_URL",
        "DEFAULT_LANGUAGE",
    ]:
        os.environ.pop(key, None)


@pytest.fixture
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent
