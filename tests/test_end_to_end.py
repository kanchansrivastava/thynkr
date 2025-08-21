from uuid import uuid4

from app.agent_loop import run_agent
from app.db import save_content


def test_full_agent_flow(monkeypatch):
    content_id = f"full_c_{uuid4().hex[:8]}"
    save_content(content_id, "Full test content for AI agent.")

    steps_responses = [
        {"action": "summarize", "input": "Full test content for AI agent."},
        {
            "action": "ask_about_content",
            "input": {"content_id": content_id, "query": "Summarize content"},
        },
        {"action": "final", "input": "Summary: Full test content."},
    ]

    def fake_plan_next_step(user_query, steps):
        # pop predetermined steps regardless of inputs
        return steps_responses.pop(0)

    monkeypatch.setattr("app.agent_loop.plan_next_step", fake_plan_next_step)

    result = run_agent("Run full AI agent workflow")
    assert "Summary: Full test content." in result
