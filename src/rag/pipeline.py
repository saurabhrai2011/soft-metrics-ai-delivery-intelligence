from src.agents.orchestrator import DeliveryIntelligenceAgent


def answer_question(question: str) -> dict:
	agent = DeliveryIntelligenceAgent()
	return agent.run(question)