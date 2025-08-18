import logging
from functools import lru_cache
from typing import Optional

from anthropic import Anthropic, APIStatusError
from fastapi import HTTPException


import json
import re

from app.config import get_settings

logger = logging.getLogger(__name__)


class ClaudeError(Exception):
    """Custom exception for Claude API-related errors."""
    pass


@lru_cache()
def get_anthropic_client() -> Anthropic:
    """Create and cache the Anthropic client."""
    settings = get_settings()
    return Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def truncate(text, max_len=300):
    """
    Shortens text for prompt history.
    Keeps beginning and end to preserve context.
    """
    if not isinstance(text, str):
        text = str(text)
    if len(text) <= max_len:
        return text
    return text[:max_len//2] + " ... " + text[-max_len//2:]



def parse_json_safely(raw_text):
    """
    Extract and parse JSON from raw LLM output.
    Raises ValueError if it can't parse.
    """
    try:
        # Try direct JSON first
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback: extract the first {...} block from text
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Could not parse JSON from: {raw_text}")



def query_claude(
    prompt: str,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    system: Optional[str] = None,
    raise_http: bool = True
) -> str:
    """
    Query Claude API with the given prompt.

    Args:
        prompt (str): The user/system prompt to send.
        model (str, optional): Override model from settings.
        max_tokens (int, optional): Override max tokens from settings.
        temperature (float, optional): Override temperature from settings.
        system (str, optional): Override system prompt from settings.
        raise_http (bool): If True, raises FastAPI HTTPException (for API routes).
                           If False, raises ClaudeError (for non-API usage).

    Returns:
        str: The text content returned by Claude.

    Raises:
        ClaudeError | HTTPException: On API or network failure.
    """
    settings = get_settings()
    client = get_anthropic_client()

    _model = model or settings.CLAUDE_MODEL
    _max_tokens = max_tokens or settings.MAX_TOKENS
    _temperature = temperature if temperature is not None else settings.TEMPERATURE
    _system = system or settings.SYSTEM_PROMPT

    try:
        logger.info(f"Claude Request | Model={_model} | MaxTokens={_max_tokens} | Temp={_temperature}")
        logger.debug(f"Prompt:\n{prompt}")

        response = client.messages.create(
            model=_model,
            max_tokens=_max_tokens,
            temperature=_temperature,
            system=_system,
            messages=[{"role": "user", "content": prompt}],
        )

        # Token usage logging
        usage = response.usage
        logger.info(
            f"Claude token usage - input: {usage.input_tokens}, output: {usage.output_tokens}, total: {usage.input_tokens + usage.output_tokens}"
        )

        # Anthropic returns list of content blocks; pick text from first block
        text_content = response.content[0].text if response.content else ""
        logger.debug(f"Claude Response (truncated): {text_content[:300]}")
        return text_content

    except APIStatusError as e:
        logger.error(f"Claude API error: {e}")
        if raise_http:
            raise HTTPException(status_code=502, detail="LLM service unavailable")
        raise ClaudeError("LLM service unavailable") from e

    except Exception as e:
        logger.exception(f"Unexpected error calling Claude: {e}")
        if raise_http:
            raise HTTPException(status_code=500, detail="Internal LLM error")
        raise ClaudeError("Internal LLM error") from e


def plan_next_step(query, steps):
    """
    Ask the LLM what to do next, given the original query and the steps so far.
    Returns a dict like:
    {
        "action": "summarize" | "search" | "final",
        "input": "<text or query for the tool>"
    }
    """
    history_text = "\n".join([
        f"Step {i+1}: Action={s['action']}, Result={truncate(s['result'])}"
        for i, s in enumerate(steps)
    ]) or "No steps taken yet."

    prompt = f"""
You are an AI research assistant with access to the following tools:
- summarize: Summarizes text in bullet points
- ask_about_content: Answers questions about stored content
- final: Return the final answer to the user

The user query is:
{query}

Steps so far:
{history_text}

Decide the next step.
If you have enough information, choose action 'final' and return the final answer in 'input'.
Otherwise, choose the next tool to use and the text to give it as 'input'.

Respond only as a JSON object:
{{
    "action": "<tool name or 'final'>",
    "input": "<tool input or final answer>"
}}
"""

    raw_response = query_claude(prompt)
    return parse_json_safely(raw_response)
