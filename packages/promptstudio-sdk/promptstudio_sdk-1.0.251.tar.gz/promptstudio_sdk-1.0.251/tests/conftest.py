import pytest
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def api_key():
    """Fixture to provide API key from environment variables"""
    return os.getenv("PROMPTSTUDIO_API_KEY", "test_key")


@pytest.fixture
def env():
    """Fixture to provide environment from environment variables"""
    return os.getenv("PROMPTSTUDIO_ENV", "test")


@pytest.fixture
def config(api_key, env):
    """Fixture to provide configuration dictionary"""
    return {"api_key": api_key, "env": env}
