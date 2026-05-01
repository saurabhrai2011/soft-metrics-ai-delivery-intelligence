from typing import Protocol


class LLMProvider(Protocol):
	def complete(self, prompt: str, max_tokens: int = 700, temperature: float = 0.2) -> str:
		"""
		Generate a completion from the configured LLM provider.
		"""
		...
