"""
SQLAlchemy ORM models for the Mission Readiness Officer database.
"""
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, String

# Portable import: bare name works when src/backend/ is on sys.path (Docker / direct
# script execution); package path works when repo root is on sys.path (FastAPI uvicorn).
try:
    from database import Base  # type: ignore[import]
except ModuleNotFoundError:
    from src.backend.database import Base  # type: ignore[import]


class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(String, primary_key=True, index=True)
    tail_number = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)   # helicopter / fixed_wing / ground_vehicle
    platform = Column(String, nullable=False)
    unit = Column(String, nullable=True)
    base = Column(String, nullable=True)
    next_mission_window = Column(DateTime, nullable=True)
    current_status = Column(String, default="GREEN")   # GREEN / AMBER / RED


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    reading_id = Column(String, primary_key=True, index=True)
    asset_id = Column(String, ForeignKey("assets.asset_id"), nullable=False, index=True)
    tail_number = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    metric_name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    component = Column(String, nullable=True)


class ServiceRecord(Base):
    __tablename__ = "service_records"

    record_id = Column(String, primary_key=True, index=True)
    asset_id = Column(String, ForeignKey("assets.asset_id"), nullable=False, index=True)
    tail_number = Column(String, nullable=True)
    component = Column(String, nullable=True)
    maintenance_type = Column(String, nullable=True)
    technician = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    notes = Column(String, nullable=True)
    outcome = Column(String, nullable=True)
