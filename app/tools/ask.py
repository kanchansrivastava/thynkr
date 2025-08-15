from app.tools.claude_client import query_claude
from app.tools.search import search_chunks
from app.db import get_content_text

PROMPT_TEMPLATES = {
    "eli5": "Explain like I'm 5:\n\n{query}\n\nContext:\n{context}",
    "bullet": "Summarize in bullet points:\n\n{query}\n\nContext:\n{context}",
    "pros_cons": "List pros and cons:\n\n{query}\n\nContext:\n{context}",
    "default": "Answer the query:\n\n{query}\n\nContext:\n{context}"
}

def ask_about_content(content_id: str, query: str, top_k: int = 3, mode: str | None = None):
    """
    Retrieve relevant chunks of content and ask Claude a question about them.
    """
    text = get_content_text(content_id)
    if not text:
        raise ValueError("Content not found")

    chunks = search_chunks(text, query, top_k=top_k)
    context = "".join(chunks)
    template = PROMPT_TEMPLATES.get(mode, PROMPT_TEMPLATES["default"])
    prompt = template.format(query=query, context=context)

    return {
        "answer": query_claude(prompt),
        "used_chunks": len(chunks)
    }
