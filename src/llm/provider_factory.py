import os
from dotenv import load_dotenv

from src.llm.offline_provider import OfflineProvider

load_dotenv()


def get_llm_provider():
	provider = os.getenv("LLM_PROVIDER", "offline").lower()
	use_llm = os.getenv("USE_LLM", "false").lower() == "true"

	if not use_llm or provider == "offline":
		return OfflineProvider()

	if provider == "anthropic":
		from src.llm.anthropic_provider import AnthropicProvider
		return AnthropicProvider()

	return OfflineProvider()
