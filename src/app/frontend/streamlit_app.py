import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from src.services.metrics_service import (
	load_synthetic_data,
	headline_kpis,
	slip_days_by_initiative,
	defects_per_epic_by_team,
	stuck_epics_by_capability,
	cycle_time_by_month,
)
from src.rag.pipeline import answer_question


st.set_page_config(
	page_title="AI Delivery Intelligence",
	layout="wide",
)

st.title("AI Delivery Intelligence")
st.caption(
	"Grounded analysis of initiatives, capabilities, and epics — every claim cites evidence."
)

data = load_synthetic_data()
kpis = headline_kpis(data)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Initiatives", kpis["initiatives_total"])
c2.metric("Capabilities slipping", kpis["capabilities_slipping"])
c3.metric("Epics stuck >14d", kpis["epics_stuck_over_14d"])
c4.metric("Avg epic cycle time", f"{kpis['avg_epic_cycle_days']} d")

st.divider()
st.subheader("Patterns to investigate")

cA, cB = st.columns(2)
with cA:
	st.markdown("**Initiative slip — avg days past plan**")
	st.bar_chart(slip_days_by_initiative(data))

with cB:
	st.markdown("**Defects per epic, by team**")
	st.bar_chart(defects_per_epic_by_team(data))

cC, cD = st.columns(2)
with cC:
	st.markdown("**Stuck epics (>14d in current status), by capability**")
	st.bar_chart(stuck_epics_by_capability(data))

with cD:
	st.markdown("**Average epic cycle time by start month**")
	st.line_chart(cycle_time_by_month(data))

st.divider()
st.subheader("Ask the agent")

question = st.text_input(
	"Question",
	placeholder="e.g. which initiative is silently slipping its capabilities?",
)

if st.button("Generate answer", type="primary"):
	if not question.strip():
		st.warning("Type a question first.")
	else:
		with st.spinner("Agent is thinking…"):
			result = answer_question(question)

		st.markdown("### Answer")
		st.markdown(result["answer"])

		st.subheader("Agent Trace")
		st.json(result["trace"])

		st.subheader("Citation Check")
		st.json(result["citation_check"])

		st.subheader("Evidence")
		for item in result["evidence"]:
			st.markdown(f"**[{item['id']}]** {item['text']}")
