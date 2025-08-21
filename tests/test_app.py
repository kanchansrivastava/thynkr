import sqlite3

import pytest

from app.agent_loop import run_agent
from app.db import get_content_text, log_query, save_content, save_embedding
from app.tools.claude_client import parse_json_safely

# ------------------------------
# Database Tests
# ------------------------------


def test_save_and_get_content():
    save_content("c1", "Hello world")
    text = get_content_text("c1")
    assert text == "Hello world"


def test_save_duplicate_content():
    content_id = "dup_test"
    # First insert succeeds
    save_content(content_id, "First content")

    # Second insert with same content_id should raise IntegrityError
    with pytest.raises(sqlite3.IntegrityError):
        save_content(content_id, "Duplicate content")


def test_save_chunk():
    save_embedding("c1", 0, "chunk text", [0.1, 0.2])
    # No exception means success


def test_log_query():
    log_query("c1", "What is this?", "This is content c1")
    # No exception means success


def test_get_nonexistent_content():
    text = get_content_text("nonexistent_id")
    assert text is None


# ------------------------------
# Claude Client Tests
# ------------------------------


def test_parse_json_safely_valid_json():
    raw = '{"action": "final", "input": "done"}'
    data = parse_json_safely(raw)
    assert data["action"] == "final"
    assert data["input"] == "done"


def test_parse_json_safely_json_in_text():
    raw = (
        'Some text before {"action":"summarize","input":"abc"} some text after'
    )
    data = parse_json_safely(raw)
    assert data["action"] == "summarize"


def test_parse_json_safely_invalid():
    raw = "No JSON here"
    import pytest

    with pytest.raises(ValueError):
        parse_json_safely(raw)


# ------------------------------
# Agent Loop Tests
# ------------------------------


def test_run_agent_final(monkeypatch):
    """Simulate a query that returns final step immediately."""

    def fake_plan_next_step(user_query, steps):
        return {"action": "final", "input": {"text": "Test final answer"}}

    monkeypatch.setattr("app.agent_loop.plan_next_step", fake_plan_next_step)

    result = run_agent("Give final answer")
    assert "Test final answer" in result


def test_run_agent_summarize_then_final(monkeypatch):
    """Simulate summarize followed by final."""
    responses = [
        '{"action": "summarize", "input": "Some text"}',
        '{"action": "final", "input": "Done summary"}',
    ]

    def fake_plan_next_step(user_query, steps):
        # Return JSON string just like the real plan_next_step would
        return responses.pop(0)

    monkeypatch.setattr("app.agent_loop.plan_next_step", fake_plan_next_step)

    result = run_agent("Summarize this")
    assert "Done summary" in result
