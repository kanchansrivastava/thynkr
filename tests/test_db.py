import json
import os
import tempfile

import pytest

import app.db as db


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    # Create temporary file
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    monkeypatch.setattr(db, "DB_FILE", tmpfile.name)
    db.init_db()
    yield
    tmpfile.close()
    os.unlink(tmpfile.name)


def test_save_and_get_content():
    db.save_content("c1", "hello world", "file.txt")
    text = db.get_content_text("c1")
    assert text == "hello world"


def test_save_embedding_and_retrieve():
    db.save_content("c2", "text for embedding")
    embedding = [0.1, 0.2, 0.3]
    db.save_embedding("c2", 1, "chunk text", embedding)

    # Direct check via sqlite
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT embedding FROM chunks WHERE content_id='c2'"
        ).fetchone()
        assert json.loads(row[0]) == embedding


def test_log_query():
    db.save_content("c3", "some text")
    db.log_query("c3", "what is this?", "answer here")

    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT query, answer FROM query_history WHERE content_id='c3'"
        ).fetchone()
        assert row == ("what is this?", "answer here")


def test_retrieve_relevant_chunks():
    content_id = "c4"
    db.save_content(content_id, "chunky text")
    db.save_embedding(content_id, 1, "chunk1", [1.0, 0.0, 0.0])
    db.save_embedding(content_id, 2, "chunk2", [0.0, 1.0, 0.0])
    db.save_embedding(content_id, 3, "chunk3", [0.0, 0.0, 1.0])

    query_embedding = [1.0, 0.0, 0.0]
    chunks = db.retrieve_relevant_chunks(content_id, query_embedding, top_k=2)

    # Now scored_chunks = [(score, text_chunk)]
    assert chunks[0][1] == "chunk1"
    # second chunk could be chunk2 or chunk3, score is 0 for both
    assert chunks[1][1] in ("chunk2", "chunk3")
    assert len(chunks) == 2
