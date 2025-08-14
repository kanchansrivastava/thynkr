from fastapi import APIRouter, Body, HTTPException
from app.tools.claude_client import query_claude
from app.tools.search import search_chunks

router = APIRouter()

@router.post("/ask")
def ask(
    content_id: str = Body(...),
    query: str = Body(...),
    top_k: int = Body(3)
):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    top_chunks = search_chunks(content_id=content_id, query=query, top_k=top_k)
    
    if not top_chunks:
        raise HTTPException(status_code=404, detail="No relevant content found")

    context_text = "\n\n".join([chunk['text_chunk'] for chunk in top_chunks])
    prompt = f"""
    Use the following context to answer the question:
    {context_text}

    Question: {query}
    """
    answer = query_claude(prompt)

    return {
        "status": "success",
        "content_id": content_id,
        "query": query,
        "answer": answer,
        "used_chunks": len(top_chunks)
    }
