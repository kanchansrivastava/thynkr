from unittest.mock import MagicMock, patch

import pytest

from app.tools.claude_client import parse_json_safely, query_claude


def test_claude_client():
    with patch(
        "app.tools.claude_client.get_anthropic_client"
    ) as mock_get_client:
        # Create mock response content with .text attribute
        mock_text_content = MagicMock()
        mock_text_content.text = "fake response"

        # Set up the mock response
        mock_response = MagicMock()
        mock_response.content = [mock_text_content]

        # Set up the mock client
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = query_claude("Test input")
        assert result == "fake response"


def test_parse_json_safely_valid_json():
    raw = '{"action": "final", "input": "done"}'
    data = parse_json_safely(raw)
    assert data["action"] == "final"
    assert data["input"] == "done"


def test_parse_json_safely_json_in_text():
    raw = 'Before text {"action":"summarize","input":"abc"} after text'
    data = parse_json_safely(raw)
    assert data["action"] == "summarize"
    assert data["input"] == "abc"


def test_parse_json_safely_invalid():
    with pytest.raises(ValueError):
        parse_json_safely("no JSON here")
