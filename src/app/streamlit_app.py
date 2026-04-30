import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.services.metrics_service import (
	load_metrics_data,
	delivery_health_by_domain,
	bottlenecks_by_status,
	high_risk_domains,
)
from src.rag.pipeline import answer_question


st.set_page_config(
	page_title="Software Metrics AI Delivery Intelligence",
	layout="wide",
)

st.title("Software Metrics AI Delivery Intelligence")
st.caption(
	"MVP implementation: CSV + Pandas metrics service + grounded answer generation with evidence IDs."
)

df = load_metrics_data()

st.header("Delivery Health Overview")

health_df = delivery_health_by_domain(df)
risk_df = high_risk_domains(df)
bottleneck_df = bottlenecks_by_status(df)

col1, col2, col3 = st.columns(3)

with col1:
	st.metric(
    	"Average Lead Time",
    	f"{health_df['avg_lead_time_days'].mean():.1f} days",
	)

with col2:
	st.metric(
    	"Average Wait Time",
    	f"{health_df['avg_wait_time_days'].mean():.1f} days",
	)

with col3:
	st.metric(
    	"Average Commitment Reliability",
    	f"{health_df['commitment_reliability_pct'].mean():.1f}%",
	)

st.subheader("Domain Health")
st.dataframe(health_df, use_container_width=True)

st.subheader("Bottlenecks by Status")
st.dataframe(bottleneck_df, use_container_width=True)

st.subheader("Risk View")
st.dataframe(risk_df, use_container_width=True)

st.header("Ask a Delivery Intelligence Question")

example_questions = [
	"What is the delivery health summary?",
	"Which status is the biggest bottleneck?",
	"Which domains are at risk?",
	"How is commitment reliability tracking?",
	"Summarise MTTR and operational health.",
]

question = st.selectbox(
	"Choose an example question or type your own below",
	example_questions,
)

custom_question = st.text_input("Custom question")

final_question = custom_question if custom_question else question

if st.button("Generate Answer"):
	result = answer_question(final_question)

	st.subheader("Answer")
	st.write(result["answer"])

	st.subheader("Query Plan")
	st.json(result["plan"])

	st.subheader("Evidence")
	for item in result["evidence"]:
		st.markdown(f"**[{item['id']}]** {item['text']}")

	st.subheader("Citation Validation")
	st.json(result["citation_check"])