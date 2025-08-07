import logging
from functools import lru_cache

from anthropic import Anthropic, APIStatusError
from fastapi import HTTPException

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_anthropic_client() -> Anthropic:
    settings = get_settings()
    return Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def query_claude(prompt: str) -> str:
    settings = get_settings()
    client = get_anthropic_client()

    try:
        response = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
            system=settings.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        # Token usage metadata
        usage = response.usage
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens

        logger.info(
            f"Claude token usage - input: {input_tokens}, output: {output_tokens}"
        )
        return response.content[0].text

    except APIStatusError as e:
        logger.error(f"Claude API error: {e}")
        raise HTTPException(status_code=500, detail="LLM service unavailable")

    except Exception as e:
        logger.exception(f"Unexpected error calling Claude : {e}")
        raise HTTPException(status_code=500, detail="Internal error")
