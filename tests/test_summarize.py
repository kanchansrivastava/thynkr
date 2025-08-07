from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_summarize_route(monkeypatch):
    def mock_claude(text):
        return "Mock summary."

    from app.api import summarize

    monkeypatch.setattr(summarize, "summarize_text", mock_claude)

    response = client.post("/summarize", json={"text": "some input"})
    assert response.status_code == 200
    assert response.json() == {"summary": "Mock summary."}
