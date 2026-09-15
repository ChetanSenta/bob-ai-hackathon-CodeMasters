"""
GET /maintenance/plan

Returns a prioritised maintenance task list: CRITICAL first, then by
mission proximity (soonest deadline first).
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
    get_action,
    get_duration,
    get_red_threshold,
    score_metric,
)
from src.backend.schemas import MaintenancePlanResponse, MaintenanceTask

router = APIRouter()

_URGENCY_MAP = {"RED": "CRITICAL", "AMBER": "HIGH"}


def _hours_until(mission_window: datetime | None) -> float | None:
    if mission_window is None:
        return None
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    delta = mission_window - now
    return round(delta.total_seconds() / 3600, 1)


@router.get("/plan", response_model=MaintenancePlanResponse)
def get_maintenance_plan(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    tasks: List[MaintenanceTask] = []

    for asset in assets:
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
            hours_available = _hours_until(asset.next_mission_window)

            tasks.append(MaintenanceTask(
                priority=0,  # assigned below after sorting
                asset_id=asset.asset_id,
                tail_number=asset.tail_number,
                platform=asset.platform,
                component=reading.component or metric_name,
                urgency=urgency,
                action=get_action(metric_name),
                estimated_duration_hours=get_duration(metric_name),
                next_mission_window=asset.next_mission_window,
                hours_available=hours_available,
            ))

    # Sort: CRITICAL first, then by hours_available ascending (most urgent deadline first)
    tasks.sort(
        key=lambda t: (
            0 if t.urgency == "CRITICAL" else 1,
            t.hours_available if t.hours_available is not None else float("inf"),
        )
    )

    # Assign 1-based priority
    for i, task in enumerate(tasks, start=1):
        task.priority = i

    return MaintenancePlanResponse(plan=tasks)
