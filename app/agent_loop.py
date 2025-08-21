import json
import logging

from app.tools.claude_client import parse_json_safely, plan_next_step

logger = logging.getLogger(__name__)


def normalize_tool_input(tool_input):
    """
    Normalize tool_input so downstream actions always receive a dict.
    - If already dict → return as is
    - If valid JSON string → load
    - Else wrap as {"text": str(tool_input)}
    """
    if isinstance(tool_input, dict):
        return tool_input
    if isinstance(tool_input, str):
        try:
            return json.loads(tool_input)
        except json.JSONDecodeError:
            return {"text": tool_input}
    return {"text": str(tool_input)}


def run_agent(user_query: str, max_steps: int = 10):
    """
    Runs the agent loop for a given user query.
    Handles LLM planning, tool execution, and final answer compilation.

    Args:
        user_query (str): The original user query.
        max_steps (int): Max steps the agent will take before giving up.

    Returns:
        str: The final answer from the agent.
    """
    steps = []

    for step_num in range(max_steps):
        try:
            # Ask LLM what to do next
            raw_step = plan_next_step(user_query, steps)

            # Parse into dict (raw may be string or dict)
            if isinstance(raw_step, str):
                next_step = parse_json_safely(raw_step)
            else:
                next_step = raw_step

            action = next_step.get("action")
            tool_input = normalize_tool_input(next_step.get("input"))

            # Handle actions
            if action == "summarize":
                text = tool_input.get("text") or tool_input.get("query")
                if not text:
                    raise ValueError("No text provided for summarization.")
                # TODO: replace placeholder with summarize function call
                summary = f"Summary of: {text[:200]}..."
                steps.append({"action": "summarize", "result": summary})

            elif action == "ask_about_content":
                content_id = tool_input.get("content_id")
                query_text = tool_input.get("query")
                if not content_id or not query_text:
                    logger.warning(
                        f"Skipping ask_about_content: Missing content_id or query. Tool input: {tool_input}"
                    )
                    steps.append(
                        {
                            "action": "ask_about_content",
                            "result": "Skipped: missing content_id or query",
                        }
                    )
                    continue

            elif action == "final":
                final_answer = (
                    tool_input.get("text")
                    or tool_input.get("answer")
                    or str(tool_input)
                )
                steps.append({"action": "final", "result": final_answer})
                return final_answer

            else:
                logger.warning(f"Unknown action received: {action}")
                steps.append({"action": "unknown", "result": str(tool_input)})

        except Exception as e:
            logger.exception(f"Error in planning next step: {e}")
            steps.append({"action": "error", "result": str(e)})

    return "Max steps reached without final answer."
