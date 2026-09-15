"""
Pydantic request / response models for all endpoints.
"""

import datetime as _dt
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------

class SensorReadingIn(BaseModel):
    reading_id: str
    asset_id: str
    tail_number: Optional[str] = None
    timestamp: _dt.datetime
    metric_name: str
    value: float
    unit: Optional[str] = None
    component: Optional[str] = None


class SensorIngestRequest(BaseModel):
    readings: List[SensorReadingIn]


class IngestResponse(BaseModel):
    ingested: int
    errors: List[str] = Field(default_factory=list)


class ServiceRecordIn(BaseModel):
    record_id: str
    asset_id: str
    tail_number: Optional[str] = None
    component: Optional[str] = None
    maintenance_type: Optional[str] = None
    technician: Optional[str] = None
    date: Optional[_dt.date] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None


class ServiceRecordIngestRequest(BaseModel):
    records: List[ServiceRecordIn]


# ---------------------------------------------------------------------------
# Readiness
# ---------------------------------------------------------------------------

class ComponentStatus(BaseModel):
    component: str
    metric: str
    value: float
    status: str        # GREEN / AMBER / RED
    score: int         # 0–100


class AssetReadinessSummary(BaseModel):
    asset_id: str
    tail_number: str
    platform: str
    asset_type: str
    unit: Optional[str] = None
    base: Optional[str] = None
    next_mission_window: Optional[_dt.datetime] = None
    overall_status: str
    overall_score: int
    components: List[ComponentStatus]


class FleetSummary(BaseModel):
    total: int
    GREEN: int
    AMBER: int
    RED: int


class FleetReadinessResponse(BaseModel):
    fleet: List[AssetReadinessSummary]
    summary: FleetSummary


class SensorReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reading_id: str
    asset_id: str
    tail_number: Optional[str] = None
    timestamp: _dt.datetime
    metric_name: str
    value: float
    unit: Optional[str] = None
    component: Optional[str] = None


class ServiceRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    record_id: str
    asset_id: str
    tail_number: Optional[str] = None
    component: Optional[str] = None
    maintenance_type: Optional[str] = None
    technician: Optional[str] = None
    date: Optional[_dt.date] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None


class AssetDetailResponse(BaseModel):
    asset_id: str
    tail_number: str
    platform: str
    asset_type: str
    unit: Optional[str] = None
    base: Optional[str] = None
    next_mission_window: Optional[_dt.datetime] = None
    overall_status: str
    overall_score: int
    components: List[ComponentStatus]
    recent_readings: List[SensorReadingOut]
    service_history: List[ServiceRecordOut]
    explanation: str


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------

class FailurePrediction(BaseModel):
    asset_id: str
    tail_number: str
    platform: str
    component: str
    metric: str
    current_value: float
    threshold_red: Optional[float]
    urgency: str           # CRITICAL / HIGH / MEDIUM
    next_mission_window: Optional[_dt.datetime]
    hours_until_mission: Optional[float]
    recommendation: str


class PredictionsResponse(BaseModel):
    predictions: List[FailurePrediction]


# ---------------------------------------------------------------------------
# Maintenance plan
# ---------------------------------------------------------------------------

class MaintenanceTask(BaseModel):
    priority: int
    asset_id: str
    tail_number: str
    platform: str
    component: str
    urgency: str
    action: str
    estimated_duration_hours: float
    next_mission_window: Optional[_dt.datetime]
    hours_available: Optional[float]


class MaintenancePlanResponse(BaseModel):
    plan: List[MaintenanceTask]
