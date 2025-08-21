from typing import List

CHUNK_SIZE = 300


def approximate_token_count(text: str) -> int:
    # Approximate 1 token ≈ 0.75 words (safe for Claude)
    words = text.split()
    return int(len(words) / 0.75)


def chunk_text(
    text: str, max_tokens: int = 300, overlap_words: int = 20
) -> List[str]:
    words = text.split()
    approx_tokens = approximate_token_count(text)

    if approx_tokens <= max_tokens:
        return [text.strip()]

    chunks = []
    start = 0
    while start < len(words):
        end = start + int(max_tokens * 0.75)
        chunk = " ".join(words[start:end])
        chunks.append(chunk.strip())

        # move window forward with overlap
        start = end - overlap_words

    return chunks
