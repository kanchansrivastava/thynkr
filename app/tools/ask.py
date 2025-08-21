from app.db import retrieve_relevant_chunks
from app.tools.claude_client import query_claude
from app.tools.search import embed_query

PROMPT_TEMPLATES = {
    "eli5": "Explain like I'm 5:\n\n{query}\n\nContext:\n{context}",
    "bullet": "Summarize in bullet points:\n\n{query}\n\nContext:\n{context}",
    "pros_cons": "List pros and cons:\n\n{query}\n\nContext:\n{context}",
    "default": "Answer the query:\n\n{query}\n\nContext:\n{context}",
}


def ask_about_content(content_id: str, query: str):
    # Get embedding for the query
    query_embedding = embed_query(query)

    # Fetch relevant chunks only for this content_id
    relevant_chunks = retrieve_relevant_chunks(content_id, query_embedding)

    # Prepare context text
    context_text = "\n".join([chunk[1] for chunk in relevant_chunks])

    # Ask Claude
    answer = query_claude(f"Context:\n{context_text}\n\nQuestion: {query}")

    return {
        "answer": answer,
        "relevant_chunks": [chunk[1] for chunk in relevant_chunks],
    }
