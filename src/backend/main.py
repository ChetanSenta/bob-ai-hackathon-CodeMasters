"""
Mission Readiness Officer — FastAPI entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.routers import ingest, readiness, predictions, maintenance

app = FastAPI(
    title="Mission Readiness Officer API",
    description="HUMS sensor ingestion, readiness scoring, and predictive maintenance endpoints.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(readiness.router, prefix="/readiness", tags=["readiness"])
app.include_router(predictions.router, prefix="/predict", tags=["predictions"])
app.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "Mission Readiness Officer API"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
