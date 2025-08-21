from app.agent_loop import run_agent
from app.db import save_content


def test_run_agent_final(monkeypatch):
    # Fake plan_next_step always returns "final" action
    def fake_plan_next_step(user_query, steps):
        return {"action": "final", "input": {"text": "Test final answer"}}

    monkeypatch.setattr("app.agent_loop.plan_next_step", fake_plan_next_step)

    result = run_agent("Give final answer")
    assert "Test final answer" in result


def test_run_agent_summarize_then_final(monkeypatch):
    responses = [
        {"action": "summarize", "input": {"text": "Some text"}},
        {"action": "final", "input": {"text": "Done summary"}},
    ]

    def fake_plan_next_step(user_query, steps):
        return responses.pop(0)

    monkeypatch.setattr("app.agent_loop.plan_next_step", fake_plan_next_step)

    result = run_agent("Summarize this")
    assert "Done summary" in result


def test_run_agent_ask_about_content(monkeypatch):
    save_content("test_c", "Some AI content")
    responses = [
        {
            "action": "ask_about_content",
            "input": {"content_id": "test_c", "query": "Give key points"},
        },
        {"action": "final", "input": {"text": "Key points returned"}},
    ]

    def fake_plan_next_step(user_query, steps):
        return responses.pop(0)

    monkeypatch.setattr("app.agent_loop.plan_next_step", fake_plan_next_step)

    result = run_agent("Explain AI content")
    assert "Key points returned" in result
