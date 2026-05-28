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

slip_df = slip_days_by_initiative(data).reset_index()
defects_df = defects_per_epic_by_team(data).reset_index()
stuck_df = stuck_epics_by_capability(data).reset_index()
cycle_df = cycle_time_by_month(data).reset_index()

cA, cB = st.columns(2)
with cA:
	st.markdown("**Initiative slip — avg days past plan**")
	st.dataframe(
		slip_df,
		column_config={
			"initiative_name": st.column_config.TextColumn("Initiative"),
			"slip_days": st.column_config.ProgressColumn(
				"Slip (days)",
				min_value=0,
				max_value=float(max(1.0, slip_df["slip_days"].max())),
				format="%.1f",
			),
		},
		hide_index=True,
		width="stretch",
	)

with cB:
	st.markdown("**Defects per epic, by team**")
	st.dataframe(
		defects_df,
		column_config={
			"team": st.column_config.TextColumn("Team"),
			"avg_defects_per_epic": st.column_config.ProgressColumn(
				"Defects / epic",
				min_value=0,
				max_value=float(max(1.0, defects_df["avg_defects_per_epic"].max())),
				format="%.2f",
			),
		},
		hide_index=True,
		width="stretch",
	)

cC, cD = st.columns(2)
with cC:
	st.markdown("**Stuck epics (>14d in current status), by capability**")
	st.dataframe(
		stuck_df,
		column_config={
			"capability_name": st.column_config.TextColumn("Capability"),
			"stuck_epics": st.column_config.ProgressColumn(
				"Stuck epics",
				min_value=0,
				max_value=int(max(1, stuck_df["stuck_epics"].max())),
				format="%d",
			),
		},
		hide_index=True,
		width="stretch",
	)

with cD:
	st.markdown("**Average epic cycle time by start month**")
	st.dataframe(
		cycle_df,
		column_config={
			"month": st.column_config.TextColumn("Month"),
			"avg_cycle_time_days": st.column_config.ProgressColumn(
				"Avg cycle time (days)",
				min_value=0,
				max_value=float(max(1.0, cycle_df["avg_cycle_time_days"].max())),
				format="%.1f",
			),
		},
		hide_index=True,
		width="stretch",
	)

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
