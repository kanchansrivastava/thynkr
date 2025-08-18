import json
import logging
from app.tools.claude_client import query_claude, plan_next_step
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


# MAX_STEPS = 5

# def run_agent(user_input: str):
#     tool_descriptions = "\n".join(f"{name}: {meta['description']}" for name, meta in TOOLS.items())
#     context = SYSTEM_PROMPT.format(tools=tool_descriptions)

#     current_input = user_input
#     steps = []

#     for step in range(MAX_STEPS):
#         prompt = f"{context}\n\nUser request: {current_input}"
#         response = query_claude(prompt)

#         try:
#             action_data = json.loads(response)
#         except json.JSONDecodeError:
#             current_input = f"Invalid JSON: {response}. Please return valid JSON."
#             continue

#         action = action_data.get("action")
#         action_input = action_data.get("input")

#         if action == "final_answer":
#             return {
#                 "steps": steps,
#                 "final_answer": action_input
#             }

#         if action not in TOOLS:
#             current_input = f"Unknown tool '{action}'. Please choose a valid tool."
#             continue

#         if isinstance(action_input, dict):
#             result = TOOLS[action]["function"](**action_input)
#         else:
#             result = TOOLS[action]["function"](action_input)

#         steps.append({"action": action, "input": action_input, "result": result})

#         current_input = f"Tool '{action}' returned: {result}"

#     return {
#         "steps": steps,
#         "final_answer": "Max steps reached without final answer."
#     }

MAX_STEPS = 5

def run_agent(initial_query):
    steps = []
    query = initial_query
    last_action = None

    for step_num in range(MAX_STEPS):
        # 1. Ask the planner for the next step
        plan = plan_next_step(query, steps)

        action = plan.get("action")
        action_input = plan.get("input")

        # 2. Stop condition: Planner says "final"
        if action == "final":
            return {
                "steps": steps,
                "final_answer": action_input
            }

        # 3. Prevent infinite repetition of same action & input
        if last_action == (action, action_input):
            return {
                "steps": steps,
                "final_answer": f"Stopped — same step '{action}' repeated twice."
            }
        last_action = (action, action_input)

        # 4. Validate input before tool call
        if not action_input or len(action_input.strip()) < 5:
            steps.append({
                "action": action,
                "input": action_input,
                "result": "Skipped — insufficient input."
            })
            continue

        # 5. Run the tool
        try:
            result = TOOLS[action]["function"](action_input)
        except Exception as e:
            result = f"Error: {e}"

        # 6. Log the step
        steps.append({
            "action": action,
            "input": action_input,
            "result": result
        })

        # 7. Check if result should be the final answer
        if isinstance(result, str) and "final answer" in result.lower():
            return {
                "steps": steps,
                "final_answer": result
            }

    # 8. Safety stop
    return {
        "steps": steps,
        "final_answer": "Max steps reached without final answer."
    }
