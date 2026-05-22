"""Claude with tool-calling. Single entry point: run_agent()."""

from __future__ import annotations
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5") # or claude-opus-4-7 if you want top quality

def run_agent(user_question: str, tools: list[dict], tool_handlers: dict, system: str, max_iters: int = 6) -> dict:
    """
    Run a tool-calling loop. Returns {"answer": str, "trace": list[dict]}.

    tools:         Anthropic tool schemas (list of dicts with name/description/input_schema)
    tool_handlers: {tool_name: callable(input_dict) -> str}
    system:        system prompt
    """
    messages = [{"role": "user", "content": user_question}]
    trace = []

    for _ in range(max_iters):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=system,
            tools=tools,
            messages=messages,
        )
        trace.append({"stop_reason": resp.stop_reason, "content": [b.model_dump() for b in resp.content]})

        if resp.stop_reason == "end_turn":
            text = "".join(b.text for b in resp.content if b.type == "text")
            return {"answer": text, "trace": trace}

        if resp.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    try:
                        result = tool_handlers[block.name](block.input)
                    except Exception as e:
                        result = f"ERROR: {e}"
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        break  # any other stop_reason: bail

    return {"answer": "Agent did not converge within max_iters.", "trace": trace}