# app/tools/summarize.py

from app.tools.claude_client import query_claude

PROMPT_TEMPLATES = {
    "eli5": "Explain like I'm 5:\n\n{query}",
    "bullet": "Summarize in bullet points:\n\n{query}",
    "pros_cons": "List pros and cons:\n\n{query}",
    "default": "Summarize the text:\n\n{query}",
}


def summarize_text(text, mode: str = "bullet"):
    template = PROMPT_TEMPLATES.get(mode, PROMPT_TEMPLATES["default"])
    prompt = template.format(query=text)
    return query_claude(prompt)
