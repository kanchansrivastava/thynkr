import json
import logging
from app.tools.claude_client import query_claude, ClaudeError
from app.tools.tool_registry import TOOLS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AGENT] %(message)s",
    handlers=[logging.FileHandler("logs/agent.log"), logging.StreamHandler()]
)

SYSTEM_PROMPT = """
You are an AI assistant with access to the following tools:

{tools}

When deciding what to do:
1. Think step-by-step.
2. Output a JSON object with exactly:
   - "action": tool name
   - "input": the input for the tool
3. Do NOT output explanations outside JSON.

Example:
{{"action": "summarize", "input": "Some text here"}}
"""

def run_agent(user_input: str, max_loops: int = 3):
    tool_descriptions = "\n".join(f"{name}: {meta['description']}" for name, meta in TOOLS.items())
    loop_count = 0
    current_input = user_input

    while loop_count < max_loops:
        loop_count += 1
        logging.info(f"Loop {loop_count} | User input: {current_input}")
        try:
            prompt = SYSTEM_PROMPT.format(tools=tool_descriptions) + f"\n\nUser request: {current_input}"
            claude_output = query_claude(prompt, max_tokens=200)

            logging.info(f"Claude raw output: {claude_output}")

            # Try to parse JSON from Claude
            try:
                parsed = json.loads(claude_output)
                action = parsed.get("action")
                tool_input = parsed.get("input")
            except json.JSONDecodeError:
                logging.error("Claude did not return valid JSON. Stopping.")
                break

            if action not in TOOLS:
                logging.error(f"Invalid tool: {action}")
                break

            # Run selected tool
            result = TOOLS[action]["function"](tool_input)
            logging.info(f"Tool result: {result}")

            # Decide if done or continue
            if action != "ask":  # Simplified stopping rule
                return result
            else:
                current_input = result
        except ClaudeError as e:
            logging.error(f"Claude error: {e}")
            break

    return {"status": "done", "data": None}
