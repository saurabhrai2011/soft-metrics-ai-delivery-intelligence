"""Claude with tool-calling. Single entry point: run_agent()."""

from __future__ import annotations
import os
from contextlib import nullcontext
from anthropic import Anthropic
from src.observability.tracing import get_langfuse, propagate_attributes

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5")


def run_agent(user_question: str, tools: list[dict], tool_handlers: dict, system: str,
              max_iters: int = 6, user_id: str | None = None, session_id: str | None = None,
              source: str | None = None) -> dict:
    """
    Run a tool-calling loop. Returns {"answer": str, "trace": list[dict]}.

    tools:         Anthropic tool schemas (list of dicts with name/description/input_schema)
    tool_handlers: {tool_name: callable(input_dict) -> str}
    system:        system prompt
    user_id:       optional Langfuse user identifier for the trace
    session_id:    optional Langfuse session identifier for the trace
    source:        optional origin label (e.g. "ui", "eval", "cli") added as a Langfuse tag
    """
    lf = get_langfuse()
    observe = lf.start_as_current_observation if lf else lambda **_: nullcontext()

    messages = [{"role": "user", "content": user_question}]
    trace = []
    answer = "Agent did not converge within max_iters."

    # propagate_attributes must be entered before the root span so user/session/tags
    # apply to every observation in the trace; no-op when Langfuse is disabled.
    attrs = (propagate_attributes(trace_name="delivery-agent", user_id=user_id, session_id=session_id,
                                  tags=[source] if source else None)
             if lf else nullcontext())

    with attrs, observe(name="delivery-agent", as_type="agent", input={"question": user_question}):
        for i in range(max_iters):
            with observe(name=f"claude-turn-{i + 1}", as_type="generation", model=MODEL,
                         model_parameters={"max_tokens": 2048}, input=messages):
                resp = client.messages.create(
                    model=MODEL, max_tokens=2048, system=system, tools=tools, messages=messages,
                )
                if lf:
                    lf.update_current_generation(
                        output=[b.model_dump() for b in resp.content],
                        usage_details={"input": resp.usage.input_tokens, "output": resp.usage.output_tokens},
                    )

            trace.append({"stop_reason": resp.stop_reason, "content": [b.model_dump() for b in resp.content]})

            if resp.stop_reason == "end_turn":
                answer = "".join(b.text for b in resp.content if b.type == "text")
                if lf:
                    lf.update_current_span(output={"answer": answer})
                break

            if resp.stop_reason != "tool_use":
                break  # any other stop_reason: bail

            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for block in (b for b in resp.content if b.type == "tool_use"):
                with observe(name=f"tool:{block.name}", as_type="tool", input=block.input):
                    try:
                        result = tool_handlers[block.name](block.input)
                    except Exception as e:
                        result = f"ERROR: {e}"
                    if lf:
                        lf.update_current_span(output={"result": result[:500] if isinstance(result, str) else result})
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(result)})
            messages.append({"role": "user", "content": tool_results})

    if lf:
        lf.flush()

    return {"answer": answer, "trace": trace}
