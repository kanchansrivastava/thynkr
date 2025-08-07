from anthropic import Anthropic
from functools import lru_cache
from app.config import get_settings


@lru_cache()
def get_anthropic_client() -> Anthropic:
    settings = get_settings()
    return Anthropic(api_key=settings.ANTHROPIC_API_KEY)



def query_claude(prompt: str) -> str:
    settings = get_settings()
    client = get_anthropic_client()
    response = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=settings.MAX_TOKENS,
        temperature=settings.TEMPERATURE,
        system=settings.SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text
