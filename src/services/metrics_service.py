import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/sample/software_metrics_sample.csv")


def load_metrics_data() -> pd.DataFrame:
	return pd.read_csv(DATA_PATH)


def delivery_health_by_domain(df: pd.DataFrame) -> pd.DataFrame:
	result = (
    	df.groupby("domain")
    	.agg(
        	avg_lead_time_days=("lead_time_days", "mean"),
        	avg_cycle_time_days=("cycle_time_days", "mean"),
        	avg_wait_time_days=("wait_time_days", "mean"),
        	total_throughput=("throughput", "sum"),
        	total_incidents=("incident_count", "sum"),
        	total_defects=("defect_count", "sum"),
        	avg_mttr_hours=("mttr_hours", "mean"),
        	commitment_target=("commitment_target", "sum"),
        	commitment_actual=("commitment_actual", "sum"),
    	)
    	.reset_index()
	)

	result["commitment_reliability_pct"] = (
    	result["commitment_actual"] / result["commitment_target"] * 100
	).round(1)

	return result.round(1)


def bottlenecks_by_status(df: pd.DataFrame) -> pd.DataFrame:
	return (
    	df.groupby("status")
    	.agg(
        	avg_wait_time_days=("wait_time_days", "mean"),
        	count=("epic_id", "count"),
    	)
    	.reset_index()
    	.sort_values("avg_wait_time_days", ascending=False)
    	.round(1)
	)


def high_risk_domains(df: pd.DataFrame) -> pd.DataFrame:
	health = delivery_health_by_domain(df)

	def risk_label(row):
		if row["commitment_reliability_pct"] < 70 or row["avg_wait_time_days"] >= 8:
			return "High"
		if row["commitment_reliability_pct"] < 85 or row["avg_wait_time_days"] >= 5:
			return "Medium"
		return "Low"

	health["risk_level"] = health.apply(risk_label, axis=1)
	return health.sort_values(
    	["risk_level", "avg_wait_time_days"],
    	ascending=[True, False],
	)


def get_metric_summary(df: pd.DataFrame) -> dict:
	health = delivery_health_by_domain(df)
	bottlenecks = bottlenecks_by_status(df)
	risks = high_risk_domains(df)

	return {
    	"health": health,
    	"bottlenecks": bottlenecks,
    	"risks": risks,
	}