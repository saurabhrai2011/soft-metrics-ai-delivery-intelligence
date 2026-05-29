from src.agents.orchestrator import DeliveryIntelligenceAgent


def answer_question(question: str, user_id: str | None = None, session_id: str | None = None,
                    source: str | None = None) -> dict:
	agent = DeliveryIntelligenceAgent()
	return agent.run(question, user_id=user_id, session_id=session_id, source=source)
