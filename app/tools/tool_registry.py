from app.tools.ask import ask_about_content
from app.tools.summarize import summarize_text

TOOLS = {
    "summarize": {
        "description": "Summarize provided text",
        "function": summarize_text,
    },
    "ask_about_content": {
        "description": "Answer a question based on saved content",
        "function": ask_about_content,
    },
    "rephrase": {
        "description": "Reword the given text in simpler language",
        "function": lambda text: summarize_text(text, mode="eli5"),
    },
}
