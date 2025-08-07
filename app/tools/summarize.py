from app.tools.claude_client import query_claude

def summarize_text(text: str) -> str:
    with open("app/prompts/summarize.txt") as f:
        prompt = f.read().replace("{{ user_input }}", text)
    return query_claude(prompt)
