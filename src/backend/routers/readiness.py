"""
GET /readiness/fleet
GET /readiness/asset/{asset_id}
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models import Asset, SensorReading, ServiceRecord
from src.backend.rules_engine import asset_overall, score_asset_components
from src.backend.schemas import (
    AssetDetailResponse,
    AssetReadinessSummary,
    FleetReadinessResponse,
    FleetSummary,
    SensorReadingOut,
    ServiceRecordOut,
)
from src.backend.watsonx_client import generate_explanation

router = APIRouter()


def _build_asset_summary(asset: Asset, db: Session) -> AssetReadinessSummary:
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.asset_id == asset.asset_id)
        .order_by(SensorReading.timestamp.desc())
        .all()
    )
    reading_dicts = [
        {"metric_name": r.metric_name, "value": r.value, "component": r.component}
        for r in readings
    ]
    components = score_asset_components(reading_dicts)
    overall_status, overall_score = asset_overall(components)

    return AssetReadinessSummary(
        asset_id=asset.asset_id,
        tail_number=asset.tail_number,
        platform=asset.platform,
        asset_type=asset.asset_type,
        unit=asset.unit,
        base=asset.base,
        next_mission_window=asset.next_mission_window,
        overall_status=overall_status,
        overall_score=overall_score,
        components=components,
    )


# ---------------------------------------------------------------------------
# GET /readiness/fleet
# ---------------------------------------------------------------------------

@router.get("/fleet", response_model=FleetReadinessResponse)
def get_fleet_readiness(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    fleet: List[AssetReadinessSummary] = [_build_asset_summary(a, db) for a in assets]

    counts = {"GREEN": 0, "AMBER": 0, "RED": 0}
    for a in fleet:
        counts[a.overall_status] = counts.get(a.overall_status, 0) + 1

    summary = FleetSummary(
        total=len(fleet),
        GREEN=counts["GREEN"],
        AMBER=counts["AMBER"],
        RED=counts["RED"],
    )
    return FleetReadinessResponse(fleet=fleet, summary=summary)


# ---------------------------------------------------------------------------
# GET /readiness/asset/{asset_id}
# ---------------------------------------------------------------------------

@router.get("/asset/{asset_id}", response_model=AssetDetailResponse)
def get_asset_readiness(asset_id: str, db: Session = Depends(get_db)):
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found")

    readings = (
        db.query(SensorReading)
        .filter(SensorReading.asset_id == asset_id)
        .order_by(SensorReading.timestamp.desc())
        .limit(50)
        .all()
    )
    service_records = (
        db.query(ServiceRecord)
        .filter(ServiceRecord.asset_id == asset_id)
        .order_by(ServiceRecord.date.desc())
        .all()
    )

    reading_dicts = [
        {"metric_name": r.metric_name, "value": r.value, "component": r.component}
        for r in readings
    ]
    components = score_asset_components(reading_dicts)
    overall_status, overall_score = asset_overall(components)

    asset_data = {
        "asset_id": asset.asset_id,
        "platform": asset.platform,
        "overall_status": overall_status,
        "overall_score": overall_score,
        "components": components,
    }
    explanation = generate_explanation(asset_data)

    return AssetDetailResponse(
        asset_id=asset.asset_id,
        tail_number=asset.tail_number,
        platform=asset.platform,
        asset_type=asset.asset_type,
        unit=asset.unit,
        base=asset.base,
        next_mission_window=asset.next_mission_window,
        overall_status=overall_status,
        overall_score=overall_score,
        components=components,
        recent_readings=[SensorReadingOut.model_validate(r) for r in readings],
        service_history=[ServiceRecordOut.model_validate(r) for r in service_records],
        explanation=explanation,
    )
