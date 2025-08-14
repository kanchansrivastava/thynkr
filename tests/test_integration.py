import pytest

from app.tools.claude_client import query_claude


@pytest.mark.integration
def test_real_claude():
    result = query_claude("FastAPI is a modern Python web framework...")
    assert "fastapi" in result.lower()
