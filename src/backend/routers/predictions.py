"""
GET /predict/failures

Returns components that are RED (already failing) or AMBER (at risk),
ranked by urgency then by mission proximity.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models import Asset, SensorReading
from src.backend.rules_engine import (
    THRESHOLDS,
    get_recommendation,
    get_red_threshold,
    score_metric,
)
from src.backend.schemas import FailurePrediction, PredictionsResponse

router = APIRouter()

_URGENCY_MAP = {"RED": "CRITICAL", "AMBER": "HIGH"}


def _hours_until(mission_window: datetime | None) -> float | None:
    if mission_window is None:
        return None
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    delta = mission_window - now
    return round(delta.total_seconds() / 3600, 1)


@router.get("/failures", response_model=PredictionsResponse)
def predict_failures(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    predictions: List[FailurePrediction] = []

    for asset in assets:
        # Latest reading per metric for this asset
        latest_by_metric: dict = {}
        readings = (
            db.query(SensorReading)
            .filter(SensorReading.asset_id == asset.asset_id)
            .order_by(SensorReading.timestamp.desc())
            .all()
        )
        for r in readings:
            if r.metric_name not in latest_by_metric:
                latest_by_metric[r.metric_name] = r

        for metric_name, reading in latest_by_metric.items():
            if metric_name not in THRESHOLDS:
                continue
            status, _score = score_metric(metric_name, reading.value)
            if status not in ("RED", "AMBER"):
                continue

            urgency = _URGENCY_MAP[status]
            hours_until = _hours_until(asset.next_mission_window)
            red_threshold = get_red_threshold(metric_name)

            predictions.append(FailurePrediction(
                asset_id=asset.asset_id,
                tail_number=asset.tail_number,
                platform=asset.platform,
                component=reading.component or metric_name,
                metric=metric_name,
                current_value=reading.value,
                threshold_red=red_threshold,
                urgency=urgency,
                next_mission_window=asset.next_mission_window,
                hours_until_mission=hours_until,
                recommendation=get_recommendation(metric_name),
            ))

    # Sort: CRITICAL first, then by hours_until_mission ascending (soonest first)
    predictions.sort(
        key=lambda p: (
            0 if p.urgency == "CRITICAL" else 1,
            p.hours_until_mission if p.hours_until_mission is not None else float("inf"),
        )
    )

    return PredictionsResponse(predictions=predictions)
