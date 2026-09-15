"""
Database initialisation and CSV/JSON seeder.

Usage:
    python src/backend/db_init.py            # create tables + seed if empty
    python src/backend/db_init.py --reset    # drop, recreate, and seed

Reads from:
    src/data/asset_registry.json
    src/data/sample_hums_sensors.csv
    src/data/sample_service_records.csv
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Portable sys.path setup
#
# In Docker:  __file__ == /app/db_init.py  → siblings are database.py, models.py
#             parents[0] == /app  → already on path via PYTHONPATH in Dockerfile
#             Import as: from database import ...
#
# Locally (run from src/backend/):
#             parents[0] == .../src/backend  → add it so bare imports work
#             parents[1] == .../src          → never used as a package root here
#             parents[2] == repo root        → add so "from src.backend..." also works
#
# Strategy: insert parents[0] (always valid — it's the script's own directory).
# Also insert parents[1] only if it has a grandparent (i.e. we're not already at
# the filesystem root), which covers both local "src/backend" and repo-root runs.
# ---------------------------------------------------------------------------
_here = Path(__file__).resolve().parent          # always valid: the script's dir
sys.path.insert(0, str(_here))                   # bare imports: database, models, …

_parent = _here.parent
if _parent != _here:                             # guard: not at filesystem root
    sys.path.insert(0, str(_parent))             # e.g. src/ — needed for src.backend.*
    _grandparent = _parent.parent
    if _grandparent != _parent:
        sys.path.insert(0, str(_grandparent))    # repo root — for local "python src/backend/db_init.py"

# Try Docker-style bare imports first; fall back to fully-qualified package path.
try:
    from database import Base, SessionLocal, engine          # type: ignore[import]
    from models import Asset, SensorReading, ServiceRecord   # type: ignore[import]  # noqa: F401
except ModuleNotFoundError:
    from src.backend.database import Base, SessionLocal, engine          # type: ignore[import]
    from src.backend.models import Asset, SensorReading, ServiceRecord   # type: ignore[import]  # noqa: F401


def _find_data_dir() -> Path:
    """Locate the data directory across environments.

    Search order:
    1. /app/src/data      — Docker container (COPY src/ → /app/src/)
    2. <script>/../data   — local run from src/backend/ → resolves to src/data/
    3. <repo_root>/src/data — local run from repo root
    """
    candidates = [
        Path("/app/src/data"),
        Path(__file__).resolve().parent.parent / "data",
    ]
    # Add repo-root candidate only when parents[2] safely exists
    _s = Path(__file__).resolve()
    if len(_s.parents) > 2:
        candidates.append(_s.parents[2] / "src" / "data")
    for candidate in candidates:
        if (candidate / "sample_hums_sensors.csv").exists():
            return candidate
    # Fall back to the first candidate and let the seeder warn on missing files
    return candidates[0]


DATA_DIR = _find_data_dir()
ASSET_REGISTRY = DATA_DIR / "asset_registry.json"
SENSORS_CSV = DATA_DIR / "sample_hums_sensors.csv"
SERVICE_CSV = DATA_DIR / "sample_service_records.csv"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_dt(val: str) -> datetime | None:
    val = val.strip().rstrip("Z")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return None


def _parse_date(val: str) -> date | None:
    try:
        return date.fromisoformat(val.strip())
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def seed_assets(db) -> int:
    if not ASSET_REGISTRY.exists():
        print(f"  [WARN] {ASSET_REGISTRY} not found — skipping assets")
        return 0
    with open(ASSET_REGISTRY) as f:
        registry = json.load(f)
    count = 0
    for entry in registry:
        asset_id = entry["asset_id"]
        existing = db.get(Asset, asset_id)
        nw = _parse_dt(entry.get("next_mission_window", ""))
        if existing:
            existing.tail_number = entry.get("tail_number", asset_id)
            existing.asset_type = entry.get("asset_type", "unknown")
            existing.platform = entry.get("platform", "unknown")
            existing.unit = entry.get("unit")
            existing.base = entry.get("base")
            existing.next_mission_window = nw
            existing.current_status = entry.get("current_status", "GREEN")
        else:
            db.add(Asset(
                asset_id=asset_id,
                tail_number=entry.get("tail_number", asset_id),
                asset_type=entry.get("asset_type", "unknown"),
                platform=entry.get("platform", "unknown"),
                unit=entry.get("unit"),
                base=entry.get("base"),
                next_mission_window=nw,
                current_status=entry.get("current_status", "GREEN"),
            ))
        count += 1
    db.commit()
    return count


def seed_sensors(db) -> int:
    if not SENSORS_CSV.exists():
        print(f"  [WARN] {SENSORS_CSV} not found — skipping sensor readings")
        return 0
    count = 0
    errors = 0
    with open(SENSORS_CSV, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                reading_id = row["reading_id"]
                ts = _parse_dt(row["timestamp"])
                if ts is None:
                    errors += 1
                    continue
                existing = db.get(SensorReading, reading_id)
                if not existing:
                    db.add(SensorReading(
                        reading_id=reading_id,
                        asset_id=row["asset_id"],
                        tail_number=row.get("tail_number"),
                        timestamp=ts,
                        metric_name=row["metric_name"],
                        value=float(row["value"]),
                        unit=row.get("unit"),
                        component=row.get("component"),
                    ))
                count += 1
            except Exception as exc:
                errors += 1
                print(f"  [WARN] sensor row error: {exc}")
    db.commit()
    if errors:
        print(f"  [WARN] {errors} sensor rows skipped due to errors")
    return count


def seed_service_records(db) -> int:
    if not SERVICE_CSV.exists():
        print(f"  [WARN] {SERVICE_CSV} not found — skipping service records")
        return 0
    count = 0
    errors = 0
    with open(SERVICE_CSV, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                record_id = row["record_id"]
                existing = db.get(ServiceRecord, record_id)
                if not existing:
                    db.add(ServiceRecord(
                        record_id=record_id,
                        asset_id=row["asset_id"],
                        tail_number=row.get("tail_number"),
                        component=row.get("component"),
                        maintenance_type=row.get("maintenance_type"),
                        technician=row.get("technician"),
                        date=_parse_date(row.get("date", "")),
                        notes=row.get("notes"),
                        outcome=row.get("outcome"),
                    ))
                count += 1
            except Exception as exc:
                errors += 1
                print(f"  [WARN] service record row error: {exc}")
    db.commit()
    if errors:
        print(f"  [WARN] {errors} service record rows skipped due to errors")
    return count


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    reset = "--reset" in sys.argv

    if reset:
        print("Dropping all tables …")
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped.")

    print("Creating tables …")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    try:
        print("Seeding assets …")
        n = seed_assets(db)
        print(f"  {n} assets seeded.")

        print("Seeding sensor readings …")
        n = seed_sensors(db)
        print(f"  {n} sensor readings seeded.")

        print("Seeding service records …")
        n = seed_service_records(db)
        print(f"  {n} service records seeded.")
    finally:
        db.close()

    print("Database initialisation complete.")


if __name__ == "__main__":
    main()
