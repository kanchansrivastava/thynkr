from app.tools.claude_client import query_claude
from app.tools.tool_registry import TOOLS

import json, re, json5

MAX_STEPS = 5

# -----------------------------
# Helpers
# -----------------------------
def truncate(text, max_len=300):
    if not isinstance(text, str):
        text = str(text)
    if len(text) <= max_len:
        return text
    return text[:max_len//2] + " ... " + text[-max_len//2:]


def parse_json_safely(raw_response: str):
    """
    Extract a JSON object from LLM response.
    Only fallback to 'final' if parsing fails.
    """
    import json5
    cleaned = raw_response.replace("\r", "").replace("\t", " ").strip()
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            data = json5.loads(json_str)
            # If JSON has required fields, return
            if "action" in data and "input" in data:
                return data
        except Exception as e:
            print(f"[parse_json_safely] JSON parsing failed: {e}")

    # Fallback to final action with raw text
    return {"action": "final", "input": cleaned}



# -----------------------------
# Plan next step
# -----------------------------
def plan_next_step(user_query, steps, tools, content_id="123"):
    history_text = "\n".join([
        f"Step {i+1}: Action={s['action']}, Result={truncate(s['result'])}"
        for i, s in enumerate(steps)
    ]) or "No steps taken yet."

    tool_list = "\n".join([f"{name}: {meta['description']}" for name, meta in tools.items()])

    prompt = f"""
You are an AI assistant with access to the following tools:
{tool_list}

User query:
{user_query}

Steps so far:
{history_text}

Decide the next step.
- If you have enough information, return:
  {{
    "action": "final",
    "input": "<final answer>"
  }}
- If you need to ask about stored content, return:
  {{
    "action": "ask_about_content",
    "input": {{
        "content_id": "{content_id}",
        "query": "<question related to the user query>"
    }}
  }}
- For other tools, return:
  {{
    "action": "<tool name>",
    "input": "<input text>"
  }}

Respond only as JSON.
"""
    raw_response = query_claude(prompt)
    return parse_json_safely(raw_response)


# -----------------------------
# Run Agent Loop
# -----------------------------
def run_agent(user_query):
    steps = []
    current_input = user_query
    last_action = None

    for step_num in range(MAX_STEPS):
        plan = plan_next_step(current_input, steps, TOOLS)
        action = plan.get("action")
        action_input = plan.get("input")

        # Stop if final answer
        if action == "final":
            steps.append({"action": "final", "input": action_input, "result": action_input})
            return {"steps": steps, "final_answer": action_input}

        # Unknown tool
        if action not in TOOLS:
            return {"steps": steps, "final_answer": f"Unknown tool '{action}' — stopping loop."}

        # Prevent repeated action+input
        if last_action == (action, action_input):
            return {"steps": steps, "final_answer": f"Repeated action '{action}' — stopping loop."}
        last_action = (action, action_input)

        # Skip empty or too short input
        if not action_input or len(str(action_input).strip()) < 5:
            steps.append({"action": action, "input": action_input, "result": "Skipped — insufficient input"})
            continue

        # Run the tool safely
        try:
            if isinstance(action_input, dict):
                result = TOOLS[action]["function"](**action_input)
            else:
                result = TOOLS[action]["function"](action_input)
        except Exception as e:
            result = f"Error: {e}"

        steps.append({"action": action, "input": action_input, "result": result})

        # Prepare next input
        if isinstance(result, dict) and "answer" in result:
            current_input = result["answer"]
        elif isinstance(result, str):
            current_input = result
        else:
            current_input = str(result)

    # Max steps reached
    return {"steps": steps, "final_answer": "Max steps reached without final answer."}
