from app.tools.claude_client import query_claude
from pathlib import Path
from string import Template

PROMPT_DIR = Path("app/prompts")

def summarize_text(text: str) -> str:
    prompt_template_path = PROMPT_DIR / "summarize.txt"
    template = Template(prompt_template_path.read_text())
    prompt = template.substitute(user_input=text.strip())
    return query_claude(prompt)