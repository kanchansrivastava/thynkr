from app.utils.chunker import chunk_text


def test_short_text():
    text = "This is a short sentence."
    chunks = chunk_text(text, max_tokens=100)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_long_text_chunking():
    text = "word " * 1000
    chunks = chunk_text(text, max_tokens=100, overlap_words=10)
    assert len(chunks) > 1
    assert all(isinstance(chunk, str) for chunk in chunks)


def test_overlap():
    text = " ".join([f"word{i}" for i in range(200)])
    chunks = chunk_text(text, max_tokens=50, overlap_words=5)
    for i in range(1, len(chunks)):
        prev_chunk = chunks[i - 1].split()[-5:]
        curr_chunk = chunks[i].split()[:5]
        assert prev_chunk == curr_chunk
