"""
Shared pytest configuration and fixtures for the agent evaluation suite.
"""

import os
import sys
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Add the framework root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "functional: Functional quality tests")
    config.addinivalue_line("markers", "evaluation: LLM output quality tests")
    config.addinivalue_line("markers", "rag: RAG pipeline tests")
    config.addinivalue_line("markers", "security: Security and red team tests")
    config.addinivalue_line("markers", "tool_calling: Tool calling tests")
    config.addinivalue_line("markers", "regression: Regression tests")
    config.addinivalue_line("markers", "slow: Tests that take >30 seconds")


@pytest.fixture(autouse=True)
def check_api_key():
    """Skip tests if OpenAI API key is not set."""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set — skipping live tests")
