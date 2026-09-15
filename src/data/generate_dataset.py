"""
generate_dataset.py
-------------------
Generates all three synthetic dataset files for the Mission Readiness demo:
  - sample_hums_sensors.csv     (~600 rows of sensor telemetry)
  - sample_service_records.csv  (~60 rows of maintenance history)
  - asset_registry.json         (25 asset objects)

Run:
    python src/data/generate_dataset.py

Files are written to the same directory as this script (src/data/).
"""

import csv
import json
import random
import os
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
random.seed(42)

# ---------------------------------------------------------------------------
# Reference dates
# ---------------------------------------------------------------------------
NOW = datetime(2025, 7, 15, 6, 0, 0, tzinfo=timezone.utc)   # reference "today"
SEVEN_DAYS_AGO = NOW - timedelta(days=7)
TWELVE_MONTHS_AGO = NOW - timedelta(days=365)

# ---------------------------------------------------------------------------
# Asset catalogue
# ---------------------------------------------------------------------------
ASSETS = [
    # Helicopters — AH-64 Apache
    {"asset_id": "AH01", "tail_number": "TAIL-AH01", "asset_type": "helicopter",    "platform": "AH-64 Apache",        "unit": "101st Airborne",          "base": "Fort Campbell"},
    {"asset_id": "AH02", "tail_number": "TAIL-AH02", "asset_type": "helicopter",    "platform": "AH-64 Apache",        "unit": "101st Airborne",          "base": "Fort Campbell"},
    {"asset_id": "AH03", "tail_number": "TAIL-AH03", "asset_type": "helicopter",    "platform": "AH-64 Apache",        "unit": "101st Airborne",          "base": "Fort Campbell"},
    {"asset_id": "AH04", "tail_number": "TAIL-AH04", "asset_type": "helicopter",    "platform": "AH-64 Apache",        "unit": "101st Airborne",          "base": "Fort Campbell"},  # ANOMALY: vibration RED
    {"asset_id": "AH05", "tail_number": "TAIL-AH05", "asset_type": "helicopter",    "platform": "AH-64 Apache",        "unit": "101st Airborne",          "base": "Fort Campbell"},
    # Helicopters — UH-60 Black Hawk
    {"asset_id": "UH01", "tail_number": "TAIL-UH01", "asset_type": "helicopter",    "platform": "UH-60 Black Hawk",    "unit": "82nd Airborne",           "base": "Fort Bragg"},
    {"asset_id": "UH02", "tail_number": "TAIL-UH02", "asset_type": "helicopter",    "platform": "UH-60 Black Hawk",    "unit": "82nd Airborne",           "base": "Fort Bragg"},
    {"asset_id": "UH03", "tail_number": "TAIL-UH03", "asset_type": "helicopter",    "platform": "UH-60 Black Hawk",    "unit": "82nd Airborne",           "base": "Fort Bragg"},  # ANOMALY: engine_temp RED
    {"asset_id": "UH04", "tail_number": "TAIL-UH04", "asset_type": "helicopter",    "platform": "UH-60 Black Hawk",    "unit": "82nd Airborne",           "base": "Fort Bragg"},
    {"asset_id": "UH05", "tail_number": "TAIL-UH05", "asset_type": "helicopter",    "platform": "UH-60 Black Hawk",    "unit": "82nd Airborne",           "base": "Fort Bragg"},
    # Fixed-wing — A-10 Thunderbolt II
    {"asset_id": "AW01", "tail_number": "TAIL-AW01", "asset_type": "fixed_wing",    "platform": "A-10 Thunderbolt II", "unit": "23rd Wing",               "base": "Moody AFB"},
    {"asset_id": "AW02", "tail_number": "TAIL-AW02", "asset_type": "fixed_wing",    "platform": "A-10 Thunderbolt II", "unit": "23rd Wing",               "base": "Moody AFB"},  # ANOMALY: oil_quality RED
    {"asset_id": "AW03", "tail_number": "TAIL-AW03", "asset_type": "fixed_wing",    "platform": "A-10 Thunderbolt II", "unit": "23rd Wing",               "base": "Moody AFB"},
    {"asset_id": "AW04", "tail_number": "TAIL-AW04", "asset_type": "fixed_wing",    "platform": "A-10 Thunderbolt II", "unit": "23rd Wing",               "base": "Moody AFB"},
    # Fixed-wing — C-130 Hercules
    {"asset_id": "CH01", "tail_number": "TAIL-CH01", "asset_type": "fixed_wing",    "platform": "C-130 Hercules",      "unit": "19th Airlift Wing",       "base": "Little Rock AFB"},
    {"asset_id": "CH02", "tail_number": "TAIL-CH02", "asset_type": "fixed_wing",    "platform": "C-130 Hercules",      "unit": "19th Airlift Wing",       "base": "Little Rock AFB"},
    {"asset_id": "CH03", "tail_number": "TAIL-CH03", "asset_type": "fixed_wing",    "platform": "C-130 Hercules",      "unit": "19th Airlift Wing",       "base": "Little Rock AFB"},
    {"asset_id": "CH04", "tail_number": "TAIL-CH04", "asset_type": "fixed_wing",    "platform": "C-130 Hercules",      "unit": "19th Airlift Wing",       "base": "Little Rock AFB"},  # ANOMALY: vibration AMBER + engine_temp AMBER
    # Ground vehicles — M1 Abrams
    {"asset_id": "MB01", "tail_number": "TAIL-MB01", "asset_type": "ground_vehicle", "platform": "M1 Abrams",          "unit": "3rd Infantry Division",   "base": "Fort Stewart"},
    {"asset_id": "MB02", "tail_number": "TAIL-MB02", "asset_type": "ground_vehicle", "platform": "M1 Abrams",          "unit": "3rd Infantry Division",   "base": "Fort Stewart"},
    {"asset_id": "MB03", "tail_number": "TAIL-MB03", "asset_type": "ground_vehicle", "platform": "M1 Abrams",          "unit": "3rd Infantry Division",   "base": "Fort Stewart"},  # ANOMALY: hours_since_service RED
    {"asset_id": "MB04", "tail_number": "TAIL-MB04", "asset_type": "ground_vehicle", "platform": "M1 Abrams",          "unit": "3rd Infantry Division",   "base": "Fort Stewart"},
    # Ground vehicles — M2 Bradley
    {"asset_id": "BR01", "tail_number": "TAIL-BR01", "asset_type": "ground_vehicle", "platform": "M2 Bradley",         "unit": "4th Infantry Division",   "base": "Fort Carson"},
    {"asset_id": "BR02", "tail_number": "TAIL-BR02", "asset_type": "ground_vehicle", "platform": "M2 Bradley",         "unit": "4th Infantry Division",   "base": "Fort Carson"},
    {"asset_id": "BR03", "tail_number": "TAIL-BR03", "asset_type": "ground_vehicle", "platform": "M2 Bradley",         "unit": "4th Infantry Division",   "base": "Fort Carson"},
]

ANOMALIES = {
    "AH04": {"vibration_mm_s": 8.2},                          # RED rotor imbalance
    "UH03": {"engine_temp_c": 228.0},                         # RED engine overheating
    "AW02": {"oil_quality_index": 32.0},                      # RED oil degradation
    "MB03": {"hours_since_last_service": 387.0},              # RED overdue service
    "CH04": {"vibration_mm_s": 5.8, "engine_temp_c": 198.0}, # AMBER+AMBER trending
}

# ---------------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------------
METRICS = [
    {
        "name": "vibration_mm_s",
        "unit": "mm/s",
        "healthy_range": (0.5, 3.8),
        "component_map": {
            "helicopter":     "rotor",
            "fixed_wing":     "engine",
            "ground_vehicle": "drivetrain",
        },
    },
    {
        "name": "engine_temp_c",
        "unit": "celsius",
        "healthy_range": (120.0, 175.0),
        "component_map": {
            "helicopter":     "engine",
            "fixed_wing":     "engine",
            "ground_vehicle": "engine",
        },
    },
    {
        "name": "oil_quality_index",
        "unit": "index",
        "healthy_range": (65.0, 98.0),
        "component_map": {
            "helicopter":     "hydraulics",
            "fixed_wing":     "hydraulics",
            "ground_vehicle": "engine",
        },
    },
    {
        "name": "hours_since_last_service",
        "unit": "hours",
        "healthy_range": (10.0, 180.0),
        "component_map": {
            "helicopter":     "airframe",
            "fixed_wing":     "airframe",
            "ground_vehicle": "drivetrain",
        },
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rand_timestamp(start: datetime, end: datetime) -> str:
    delta = end - start
    offset_s = random.uniform(0, delta.total_seconds())
    ts = start + timedelta(seconds=offset_s)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def healthy_value(metric: dict) -> float:
    lo, hi = metric["healthy_range"]
    return round(random.uniform(lo, hi), 2)


def jitter(base: float, pct: float = 0.03) -> float:
    """Add ±pct% noise to a base value."""
    return round(base * (1 + random.uniform(-pct, pct)), 2)


def derive_status(asset_id: str) -> str:
    """Derive current_status from injected anomalies."""
    if asset_id not in ANOMALIES:
        return "GREEN"
    vals = ANOMALIES[asset_id]
    # RED conditions
    if vals.get("vibration_mm_s", 0) > 7.0:
        return "RED"
    if vals.get("engine_temp_c", 0) > 220:
        return "RED"
    if vals.get("oil_quality_index", 100) < 40:
        return "RED"
    if vals.get("hours_since_last_service", 0) > 350:
        return "RED"
    # AMBER conditions
    if 4.0 <= vals.get("vibration_mm_s", 0) <= 7.0:
        return "AMBER"
    if 180 <= vals.get("engine_temp_c", 0) <= 220:
        return "AMBER"
    return "AMBER"

# ---------------------------------------------------------------------------
# Generate sensor readings
# ---------------------------------------------------------------------------

def generate_sensor_rows() -> list[dict]:
    rows = []
    reading_id = 1

    for asset in ASSETS:
        asset_id = asset["asset_id"]
        asset_type = asset["asset_type"]
        anomaly_vals = ANOMALIES.get(asset_id, {})

        # 6 timestamps spread over last 7 days (one per ~28 hours)
        timestamps = sorted([rand_timestamp(SEVEN_DAYS_AGO, NOW) for _ in range(6)])

        for ts in timestamps:
            for metric in METRICS:
                metric_name = metric["name"]
                component = metric["component_map"][asset_type]

                if metric_name in anomaly_vals:
                    # Use the injected anomaly value with slight per-reading jitter
                    value = jitter(anomaly_vals[metric_name], pct=0.02)
                else:
                    value = healthy_value(metric)

                rows.append({
                    "reading_id":  f"RD{reading_id:05d}",
                    "asset_id":    asset_id,
                    "tail_number": asset["tail_number"],
                    "asset_type":  asset_type,
                    "platform":    asset["platform"],
                    "timestamp":   ts,
                    "metric_name": metric_name,
                    "value":       value,
                    "unit":        metric["unit"],
                    "component":   component,
                })
                reading_id += 1

    return rows  # 25 assets × 6 timestamps × 4 metrics = 600 rows


# ---------------------------------------------------------------------------
# Generate service records
# ---------------------------------------------------------------------------

MAINTENANCE_TYPES = [
    "scheduled_inspection",
    "component_replacement",
    "lubrication",
    "calibration",
    "unscheduled_repair",
]

TECHNICIANS = [
    "SSG Torres", "CPT Nguyen", "SGT Mitchell", "WO2 Patel",
    "SGT Ramirez", "SSG Williams", "CPT Okonkwo", "SGT Hassan",
    "WO1 Chen",   "SGT Larson",
]

COMPONENTS_BY_TYPE = {
    "helicopter":     ["rotor", "engine", "hydraulics", "airframe", "avionics"],
    "fixed_wing":     ["engine", "hydraulics", "airframe", "avionics", "landing_gear"],
    "ground_vehicle": ["engine", "drivetrain", "hydraulics", "tracks", "turret"],
}

OUTCOME_WEIGHTS = {
    "completed": 0.75,
    "parts_on_order": 0.15,
    "deferred": 0.10,
}

def weighted_choice(choices: dict) -> str:
    items = list(choices.keys())
    weights = list(choices.values())
    return random.choices(items, weights=weights, k=1)[0]


def generate_service_rows() -> list[dict]:
    rows = []
    record_id = 1

    # Ensure every asset has at least 2 records; anomalous assets get special treatment
    for asset in ASSETS:
        asset_id = asset["asset_id"]
        asset_type = asset["asset_type"]
        components = COMPONENTS_BY_TYPE[asset_type]

        if asset_id == "MB03":
            # Overdue: last service was ~390 hours ago (~16 days, but only 1 old record)
            record_date = (NOW - timedelta(days=16)).strftime("%Y-%m-%d")
            rows.append({
                "record_id":        f"SR{record_id:04d}",
                "asset_id":         asset_id,
                "tail_number":      asset["tail_number"],
                "component":        "drivetrain",
                "maintenance_type": "scheduled_inspection",
                "technician":       random.choice(TECHNICIANS),
                "date":             record_date,
                "notes":            "Inspection deferred — parts unavailable. Overdue follow-up required.",
                "outcome":          "deferred",
            })
            record_id += 1
            continue

        if asset_id in ("AH04", "UH03", "AW02", "CH04"):
            # Anomalous assets: 1 recent failed/deferred record
            record_date = (NOW - timedelta(days=random.randint(3, 10))).strftime("%Y-%m-%d")
            anomaly_notes = {
                "AH04": "Elevated rotor vibration noted during post-flight check. Repair attempted; vibration persists.",
                "UH03": "Engine temperature spiked during sortie. Cooling system inspected; issue unresolved.",
                "AW02": "Oil sample showed degradation. Oil change deferred pending fresh supply delivery.",
                "CH04": "Vibration and temp trending upward. Flagged for pre-mission inspection.",
            }
            rows.append({
                "record_id":        f"SR{record_id:04d}",
                "asset_id":         asset_id,
                "tail_number":      asset["tail_number"],
                "component":        list(COMPONENTS_BY_TYPE[asset_type])[0],
                "maintenance_type": "unscheduled_repair",
                "technician":       random.choice(TECHNICIANS),
                "date":             record_date,
                "notes":            anomaly_notes[asset_id],
                "outcome":          "deferred",
            })
            record_id += 1

        # Regular maintenance history: 2–3 records per asset over past 12 months
        num_records = random.randint(2, 3)
        for _ in range(num_records):
            record_date = (NOW - timedelta(days=random.randint(14, 365))).strftime("%Y-%m-%d")
            component = random.choice(components)
            mtype = random.choice(MAINTENANCE_TYPES)
            rows.append({
                "record_id":        f"SR{record_id:04d}",
                "asset_id":         asset_id,
                "tail_number":      asset["tail_number"],
                "component":        component,
                "maintenance_type": mtype,
                "technician":       random.choice(TECHNICIANS),
                "date":             record_date,
                "notes":            f"Routine {mtype.replace('_', ' ')} completed. No anomalies detected.",
                "outcome":          weighted_choice(OUTCOME_WEIGHTS),
            })
            record_id += 1

    return rows


# ---------------------------------------------------------------------------
# Generate asset registry
# ---------------------------------------------------------------------------

def generate_asset_registry() -> list[dict]:
    registry = []
    for asset in ASSETS:
        asset_id = asset["asset_id"]
        days_offset = random.randint(2, 5)
        hours_offset = random.randint(0, 23)
        mission_window = (NOW + timedelta(days=days_offset, hours=hours_offset)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        registry.append({
            "asset_id":             asset_id,
            "tail_number":          asset["tail_number"],
            "asset_type":           asset["asset_type"],
            "platform":             asset["platform"],
            "unit":                 asset["unit"],
            "base":                 asset["base"],
            "next_mission_window":  mission_window,
            "current_status":       derive_status(asset_id),
        })
    return registry


# ---------------------------------------------------------------------------
# Write files
# ---------------------------------------------------------------------------

SENSOR_FIELDNAMES = [
    "reading_id", "asset_id", "tail_number", "asset_type", "platform",
    "timestamp", "metric_name", "value", "unit", "component",
]

SERVICE_FIELDNAMES = [
    "record_id", "asset_id", "tail_number", "component",
    "maintenance_type", "technician", "date", "notes", "outcome",
]

def write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ {path} ({len(rows)} rows)")


def write_json(path: str, data: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    print(f"  ✓ {path} ({len(data)} entries)")


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("Generating synthetic HUMS dataset …")

    sensor_rows = generate_sensor_rows()
    service_rows = generate_service_rows()
    registry = generate_asset_registry()

    write_csv(
        os.path.join(script_dir, "sample_hums_sensors.csv"),
        sensor_rows,
        SENSOR_FIELDNAMES,
    )
    write_csv(
        os.path.join(script_dir, "sample_service_records.csv"),
        service_rows,
        SERVICE_FIELDNAMES,
    )
    write_json(
        os.path.join(script_dir, "asset_registry.json"),
        registry,
    )

    print("\nSummary:")
    print(f"  Sensor readings : {len(sensor_rows)}")
    print(f"  Service records : {len(service_rows)}")
    print(f"  Asset registry  : {len(registry)} assets")
    print("\nAnomaly summary (injected values):")
    for aid, vals in ANOMALIES.items():
        status = derive_status(aid)
        print(f"  {aid} [{status}] — {vals}")
    print("\nDone.")


if __name__ == "__main__":
    main()
