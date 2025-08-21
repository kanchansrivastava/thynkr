import os
import tempfile

import pytest

import app.db as db


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    """Use a temporary SQLite database for all tests."""
    # Create temporary file
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    monkeypatch.setattr(db, "DB_FILE", tmpfile.name)
    db.init_db()
    yield
    tmpfile.close()
    os.unlink(tmpfile.name)
