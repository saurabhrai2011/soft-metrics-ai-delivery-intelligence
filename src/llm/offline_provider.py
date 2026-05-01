class OfflineProvider:
	def complete(
		self,
		prompt: str,
		max_tokens: int = 700,
		temperature: float = 0.2,
	) -> str:
		return (
			"1. Direct Answer\n"
			"The system is running in offline mode, so no external LLM call was made. "
			"The response is generated from deterministic evidence produced by the agent tools. [E1]\n\n"
			"2. Supporting Evidence\n"
			"The evidence panel contains the source metrics used by the selected tool. [E1]\n\n"
			"3. Recommended Action\n"
			"To test live LLM generation, set USE_LLM=true and provide your own ANTHROPIC_API_KEY."
		)
