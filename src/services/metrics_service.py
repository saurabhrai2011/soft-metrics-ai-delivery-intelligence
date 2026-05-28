import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DATA_PATH = PROJECT_ROOT / "data" / "sample" / "software_metrics_sample.csv"
SYNTHETIC_DIR = PROJECT_ROOT / "data" / "synthetic"


# ──────────────────────────────────────────────────────────────────────────
# Legacy sample-CSV API (still consumed by metrics_explainer / risk /
# narrative tools). New dashboard reads synthetic data via the functions
# below. Migrating the secondary tools is a follow-up.
# ──────────────────────────────────────────────────────────────────────────

def load_metrics_data() -> pd.DataFrame:
	return pd.read_csv(SAMPLE_DATA_PATH)


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


# ──────────────────────────────────────────────────────────────────────────
# Synthetic-data API: same dataset the agent's query_metrics tool reads.
# Used by the Streamlit dashboard so the numbers a user sees match what
# the agent will quote.
# ──────────────────────────────────────────────────────────────────────────

def load_synthetic_data() -> dict[str, pd.DataFrame]:
	return {
		"initiatives": pd.read_csv(SYNTHETIC_DIR / "Initiative_Extract.csv"),
		"capabilities": pd.read_csv(
			SYNTHETIC_DIR / "Capability_Extract.csv",
			parse_dates=["start_date", "planned_end_date", "actual_end_date"],
		),
		"epics": pd.read_csv(
			SYNTHETIC_DIR / "Epic_Extract.csv",
			parse_dates=["start_date", "planned_end_date", "actual_end_date"],
		),
	}


def headline_kpis(data: dict[str, pd.DataFrame]) -> dict:
	caps = data["capabilities"]
	epics = data["epics"]

	completed = caps[caps["actual_end_date"].notna()]
	slipping = completed[completed["actual_end_date"] > completed["planned_end_date"]]
	stuck = epics[epics["days_in_current_status"] > 14]

	return {
		"initiatives_total": len(data["initiatives"]),
		"capabilities_slipping": len(slipping),
		"epics_stuck_over_14d": len(stuck),
		"avg_epic_cycle_days": round(epics["cycle_time_days"].mean(), 1),
	}


def slip_days_by_initiative(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
	caps = data["capabilities"]
	inits = data["initiatives"][["initiative_id", "initiative_name"]]

	completed = caps[caps["actual_end_date"].notna()].copy()
	completed["slip_days"] = (
		completed["actual_end_date"] - completed["planned_end_date"]
	).dt.days

	result = (
		completed.groupby("initiative_id")["slip_days"]
		.mean()
		.round(1)
		.reset_index()
		.merge(inits, on="initiative_id")
		.sort_values("slip_days", ascending=False)
	)
	return result.set_index("initiative_name")[["slip_days"]]


def defects_per_epic_by_team(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
	epics = data["epics"]
	result = (
		epics.groupby("team")["defect_count"]
		.mean()
		.round(2)
		.reset_index()
		.rename(columns={"defect_count": "avg_defects_per_epic"})
		.sort_values("avg_defects_per_epic", ascending=False)
	)
	return result.set_index("team")[["avg_defects_per_epic"]]


def stuck_epics_by_capability(
	data: dict[str, pd.DataFrame],
	threshold_days: int = 14,
	top_n: int = 10,
) -> pd.DataFrame:
	epics = data["epics"]
	caps = data["capabilities"][["capability_id", "capability_name"]]

	stuck = epics[epics["days_in_current_status"] > threshold_days]
	counts = (
		stuck.groupby("capability_id")
		.size()
		.reset_index(name="stuck_epics")
		.merge(caps, on="capability_id")
		.sort_values("stuck_epics", ascending=False)
		.head(top_n)
	)
	return counts.set_index("capability_name")[["stuck_epics"]]


def cycle_time_by_month(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
	epics = data["epics"].copy()
	epics["month"] = epics["start_date"].dt.to_period("M").astype(str)
	result = (
		epics.groupby("month")["cycle_time_days"]
		.mean()
		.round(1)
		.reset_index()
		.rename(columns={"cycle_time_days": "avg_cycle_time_days"})
		.sort_values("month")
	)
	return result.set_index("month")[["avg_cycle_time_days"]]
