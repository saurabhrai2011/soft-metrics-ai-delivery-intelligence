"""Generate synthetic Initiative / Capability / Epic data with seeded patterns."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)  # reproducible

OUT_DIR = Path("data/synthetic")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Reference data ----------
TEAMS = [
    "Team Phoenix", "Team Atlas", "Team Orion", "Team Vega",
    "Team Lyra", "Team Cygnus", "Team Draco", "Team Nova",
]
OWNERS = [
    "S. Rai", "J. Chen", "M. Patel", "A. Johnson",
    "R. Kumar", "L. Nguyen", "D. Singh", "P. Wong",
]
STATUSES = ["Not Started", "In Progress", "In Review", "Done", "Blocked"]
PRIORITIES = ["P0", "P1", "P2", "P3"]

INITIATIVE_NAMES = [
    "Fiber Rollout Enterprise", "5G Core Modernization", "Network Modernization",
    "Customer Self-Service Platform", "Billing System Replatform",
    "Cloud Migration Wave 2", "Data Platform Unification", "Field Ops Automation",
    "Identity & Access Overhaul", "Wholesale API Suite", "AI Operations Pilot",
    "Security Posture Uplift", "Observability Standardization", "Edge Compute Buildout",
    "Partner Integration Hub",
]

CAPABILITY_TEMPLATES = [
    "{prefix} Platform", "{prefix} Gateway", "{prefix} Service",
    "{prefix} Pipeline", "{prefix} Console", "{prefix} Connector",
    "{prefix} Orchestrator", "{prefix} Insights",
]
CAPABILITY_PREFIXES = [
    "Order", "Provisioning", "Activation", "Diagnostics", "Billing",
    "Identity", "Customer", "Partner", "Telemetry", "Inventory",
    "Routing", "API", "Notification", "Settlement",
]

EPIC_VERBS = ["Implement", "Migrate", "Refactor", "Build", "Decommission", "Integrate", "Automate"]
EPIC_NOUNS = ["service", "endpoint", "dashboard", "ingestion job", "auth flow", "batch job", "event consumer"]

# ---------- Helpers ----------
def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 1)))

def in_q3(d: date) -> bool:
    return d.month in (7, 8, 9)

# ---------- Initiatives ----------
initiatives = []
for i, name in enumerate(INITIATIVE_NAMES, start=1):
    start = random_date(date(2025, 1, 1), date(2025, 6, 30))
    duration_days = random.randint(180, 540)
    end = start + timedelta(days=duration_days)
    initiatives.append({
        "initiative_id": f"INIT-{i:03d}",
        "initiative_name": name,
        "owner": random.choice(OWNERS),
        "start_date": start,
        "target_end_date": end,
        "budget_aud_m": round(random.uniform(2.0, 50.0), 2),
        "strategic_priority": random.choice(["High", "High", "Medium", "Low"]),
        "status": random.choice(["On Track", "On Track", "At Risk", "Delayed"]),
    })

# ---------- Capabilities ----------
capabilities = []
cap_id = 0
for init in initiatives:
    n_caps = random.randint(3, 8)
    # SEED PATTERN 1: "Network Modernization" silently slipping
    is_slipping_init = init["initiative_name"] == "Network Modernization"
    for _ in range(n_caps):
        cap_id += 1
        prefix = random.choice(CAPABILITY_PREFIXES)
        template = random.choice(CAPABILITY_TEMPLATES)
        name = template.format(prefix=prefix)
        start = random_date(init["start_date"], init["start_date"] + timedelta(days=120))
        planned_days = random.randint(60, 180)
        # Seeded slip: capabilities under Network Modernization run +30%
        actual_days = int(planned_days * (1.30 if is_slipping_init else random.uniform(0.9, 1.15)))
        capabilities.append({
            "capability_id": f"CAP-{cap_id:04d}",
            "capability_name": name,
            "initiative_id": init["initiative_id"],
            "owner": random.choice(OWNERS),
            "start_date": start,
            "planned_end_date": start + timedelta(days=planned_days),
            "actual_end_date": start + timedelta(days=actual_days),
            "status": random.choice(["In Progress", "In Progress", "Done", "At Risk"]),
            "completion_pct": random.randint(20, 100),
        })

# SEED PATTERN 3: "API Gateway Replatform" — pick one capability and mark it blocked-heavy
api_gateway_cap = random.choice([c for c in capabilities if "Gateway" in c["capability_name"]])
api_gateway_cap["capability_name"] = "API Gateway Replatform"
api_gateway_cap["status"] = "At Risk"

# ---------- Epics ----------
epics = []
epic_id = 0
for cap in capabilities:
    n_epics = random.randint(4, 12)
    is_blocked_cap = cap["capability_id"] == api_gateway_cap["capability_id"]
    for _ in range(n_epics):
        epic_id += 1
        team = random.choice(TEAMS)
        verb = random.choice(EPIC_VERBS)
        noun = random.choice(EPIC_NOUNS)
        prefix = cap["capability_name"].split()[0]
        epic_name = f"{verb} {prefix} {noun}"

        start = random_date(cap["start_date"], cap["start_date"] + timedelta(days=60))
        planned_days = random.randint(14, 60)
        # SEED PATTERN 4: Q3 slowdown (+25%)
        cycle_multiplier = 1.25 if in_q3(start) else random.uniform(0.95, 1.10)
        cycle_time_days = int(planned_days * cycle_multiplier)

        # SEED PATTERN 2: Team Phoenix has 2x defect rate
        base_defects = random.randint(0, 4)
        defects = base_defects * 2 if team == "Team Phoenix" else base_defects

        # SEED PATTERN 3: API Gateway Replatform — 60% stuck in review
        if is_blocked_cap and random.random() < 0.6:
            status = "In Review"
            days_in_status = random.randint(15, 45)  # stuck >14 days
        else:
            status = random.choice(STATUSES)
            days_in_status = random.randint(1, 14)

        epics.append({
            "epic_id": f"EPIC-{epic_id:05d}",
            "epic_name": epic_name,
            "capability_id": cap["capability_id"],
            "team": team,
            "owner": random.choice(OWNERS),
            "priority": random.choice(PRIORITIES),
            "story_points": random.choice([3, 5, 8, 13, 21]),
            "start_date": start,
            "planned_end_date": start + timedelta(days=planned_days),
            "actual_end_date": start + timedelta(days=cycle_time_days) if status == "Done" else None,
            "cycle_time_days": cycle_time_days,
            "status": status,
            "days_in_current_status": days_in_status,
            "defect_count": defects,
        })

# ---------- Write CSVs ----------
pd.DataFrame(initiatives).to_csv(OUT_DIR / "Initiative_Extract.csv", index=False)
pd.DataFrame(capabilities).to_csv(OUT_DIR / "Capability_Extract.csv", index=False)
pd.DataFrame(epics).to_csv(OUT_DIR / "Epic_Extract.csv", index=False)

print(f"Wrote {len(initiatives)} initiatives, {len(capabilities)} capabilities, {len(epics)} epics to {OUT_DIR}/")