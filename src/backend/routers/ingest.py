"""
POST /ingest/sensors
POST /ingest/service-records

Both endpoints accept either:
  - JSON body  ({"readings": [...]} / {"records": [...]})
  - multipart file upload (CSV)
"""
from __future__ import annotations

import csv
import io
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models import Asset, SensorReading, ServiceRecord
from src.backend.schemas import (
    IngestResponse,
    SensorIngestRequest,
    ServiceRecordIngestRequest,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_dt(val: str) -> Optional[datetime]:
    val = val.strip().rstrip("Z")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return None


def _parse_date(val: str) -> Optional[date]:
    try:
        return date.fromisoformat(val.strip())
    except ValueError:
        return None


def _upsert_asset_stub(db: Session, asset_id: str, tail_number: Optional[str] = None) -> None:
    """Create a minimal asset row if it doesn't already exist."""
    if not db.get(Asset, asset_id):
        db.add(Asset(
            asset_id=asset_id,
            tail_number=tail_number or asset_id,
            asset_type="unknown",
            platform="unknown",
            current_status="GREEN",
        ))


# ---------------------------------------------------------------------------
# /ingest/sensors — JSON body
# ---------------------------------------------------------------------------

@router.post("/sensors", response_model=IngestResponse)
def ingest_sensors_json(payload: SensorIngestRequest, db: Session = Depends(get_db)):
    errors: List[str] = []
    ingested = 0
    for r in payload.readings:
        try:
            _upsert_asset_stub(db, r.asset_id, r.tail_number)
            existing = db.get(SensorReading, r.reading_id)
            if existing:
                existing.timestamp = r.timestamp
                existing.metric_name = r.metric_name
                existing.value = r.value
                existing.unit = r.unit
                existing.component = r.component
            else:
                db.add(SensorReading(
                    reading_id=r.reading_id,
                    asset_id=r.asset_id,
                    tail_number=r.tail_number,
                    timestamp=r.timestamp,
                    metric_name=r.metric_name,
                    value=r.value,
                    unit=r.unit,
                    component=r.component,
                ))
            ingested += 1
        except Exception as exc:
            errors.append(f"{r.reading_id}: {exc}")
    db.commit()
    return IngestResponse(ingested=ingested, errors=errors)


# ---------------------------------------------------------------------------
# /ingest/sensors/upload — CSV multipart
# ---------------------------------------------------------------------------

@router.post("/sensors/upload", response_model=IngestResponse)
async def ingest_sensors_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    reader = csv.DictReader(io.StringIO(contents.decode("utf-8-sig")))
    errors: List[str] = []
    ingested = 0
    for row in reader:
        try:
            reading_id = row["reading_id"]
            asset_id = row["asset_id"]
            tail_number = row.get("tail_number")
            ts = _parse_dt(row["timestamp"])
            if ts is None:
                raise ValueError(f"Cannot parse timestamp: {row['timestamp']}")
            value = float(row["value"])
            _upsert_asset_stub(db, asset_id, tail_number)
            existing = db.get(SensorReading, reading_id)
            if existing:
                existing.timestamp = ts
                existing.metric_name = row["metric_name"]
                existing.value = value
                existing.unit = row.get("unit")
                existing.component = row.get("component")
            else:
                db.add(SensorReading(
                    reading_id=reading_id,
                    asset_id=asset_id,
                    tail_number=tail_number,
                    timestamp=ts,
                    metric_name=row["metric_name"],
                    value=value,
                    unit=row.get("unit"),
                    component=row.get("component"),
                ))
            ingested += 1
        except Exception as exc:
            errors.append(f"Row {ingested + len(errors) + 1}: {exc}")
    db.commit()
    return IngestResponse(ingested=ingested, errors=errors)


# ---------------------------------------------------------------------------
# /ingest/service-records — JSON body
# ---------------------------------------------------------------------------

@router.post("/service-records", response_model=IngestResponse)
def ingest_service_records_json(
    payload: ServiceRecordIngestRequest,
    db: Session = Depends(get_db),
):
    errors: List[str] = []
    ingested = 0
    for r in payload.records:
        try:
            _upsert_asset_stub(db, r.asset_id, r.tail_number)
            existing = db.get(ServiceRecord, r.record_id)
            if existing:
                existing.component = r.component
                existing.maintenance_type = r.maintenance_type
                existing.technician = r.technician
                existing.date = r.date
                existing.notes = r.notes
                existing.outcome = r.outcome
            else:
                db.add(ServiceRecord(
                    record_id=r.record_id,
                    asset_id=r.asset_id,
                    tail_number=r.tail_number,
                    component=r.component,
                    maintenance_type=r.maintenance_type,
                    technician=r.technician,
                    date=r.date,
                    notes=r.notes,
                    outcome=r.outcome,
                ))
            ingested += 1
        except Exception as exc:
            errors.append(f"{r.record_id}: {exc}")
    db.commit()
    return IngestResponse(ingested=ingested, errors=errors)


# ---------------------------------------------------------------------------
# /ingest/service-records/upload — CSV multipart
# ---------------------------------------------------------------------------

@router.post("/service-records/upload", response_model=IngestResponse)
async def ingest_service_records_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    reader = csv.DictReader(io.StringIO(contents.decode("utf-8-sig")))
    errors: List[str] = []
    ingested = 0
    for row in reader:
        try:
            record_id = row["record_id"]
            asset_id = row["asset_id"]
            tail_number = row.get("tail_number")
            _upsert_asset_stub(db, asset_id, tail_number)
            rec_date = _parse_date(row.get("date", ""))
            existing = db.get(ServiceRecord, record_id)
            if existing:
                existing.component = row.get("component")
                existing.maintenance_type = row.get("maintenance_type")
                existing.technician = row.get("technician")
                existing.date = rec_date
                existing.notes = row.get("notes")
                existing.outcome = row.get("outcome")
            else:
                db.add(ServiceRecord(
                    record_id=record_id,
                    asset_id=asset_id,
                    tail_number=tail_number,
                    component=row.get("component"),
                    maintenance_type=row.get("maintenance_type"),
                    technician=row.get("technician"),
                    date=rec_date,
                    notes=row.get("notes"),
                    outcome=row.get("outcome"),
                ))
            ingested += 1
        except Exception as exc:
            errors.append(f"Row {ingested + len(errors) + 1}: {exc}")
    db.commit()
    return IngestResponse(ingested=ingested, errors=errors)
