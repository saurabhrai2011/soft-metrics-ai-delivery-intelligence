def build_grounded_answer_prompt(
	question: str,
	evidence: list[dict],
	agent_trace: dict,
) -> str:
	evidence_text = "\n".join(
    	[f"[{item['id']}] {item['text']}" for item in evidence]
	)

	return f"""
You are an AI Delivery Intelligence Assistant for software engineering leaders.

Your job:
- Answer the user's question using ONLY the evidence provided.
- Do not invent metrics, numbers, teams, domains, or causes.
- Every factual claim must cite an evidence ID like [E1].
- If evidence is insufficient, say that clearly.
- Keep the answer concise, professional, and executive-ready.
- Include recommended actions only if they are supported by the evidence.

User question:
{question}

Agent trace:
{agent_trace}

Evidence:
{evidence_text}

Answer format:
1. Direct Answer
2. Supporting Evidence
3. Recommended Action
"""