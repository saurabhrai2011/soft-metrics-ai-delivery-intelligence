import os
from dotenv import load_dotenv
from anthropic import Anthropic

from src.llm.base import LLMProvider


load_dotenv()


class AnthropicProvider(LLMProvider):
	def __init__(self):
		self.api_key = os.getenv("ANTHROPIC_API_KEY")
		self.model = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")

		if not self.api_key:
			raise ValueError(
				"ANTHROPIC_API_KEY is missing. Add it to your .env file."
			)

		self.client = Anthropic(api_key=self.api_key)

	def complete(
		self,
		prompt: str,
		max_tokens: int = 700,
		temperature: float = 0.2,
	) -> str:
		message = self.client.messages.create(
			model=self.model,
			max_tokens=max_tokens,
			messages=[
				{
					"role": "user",
					"content": prompt,
				}
			],
		)

		# Claude responses are returned as content blocks.
		return "\n".join(
			block.text for block in message.content if hasattr(block, "text")
		)
