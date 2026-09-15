# Mission Readiness Officer — Project Rules

This workspace contains the **Mission Readiness & Predictive Maintenance** system for military fleet management.

## Project Overview
- **Backend**: FastAPI (Python) running on `http://localhost:8000`
- **Frontend**: React + Tailwind running on `http://localhost:3000`
- **MCP server**: `src/mcp/` — Node.js stdio server exposing 4 readiness tools to Bob
- **Dataset**: 25 assets (helicopters, fixed-wing, ground vehicles) with 4 sensor metrics

## MCP Tools Available
When in **🛡️ Mission Readiness Officer** mode, four tools are available via the `mission-readiness` MCP server:

| Tool | Endpoint | Use for |
|------|----------|---------|
| `get_fleet_readiness` | GET /readiness/fleet | Fleet-wide status, summary counts |
| `get_asset_detail` | GET /readiness/asset/{id} | Single asset breakdown, explanation |
| `get_failure_predictions` | GET /predict/failures | Ranked failure risk before mission |
| `get_maintenance_plan` | GET /maintenance/plan | Prioritised work orders |

## Sensor Metrics & Thresholds
| Metric | GREEN | AMBER | RED |
|--------|-------|-------|-----|
| vibration_mm_s | < 4.0 | 4.0–7.0 | > 7.0 |
| engine_temp_c | < 180°C | 180–220°C | > 220°C |
| oil_quality_index | > 60 | 40–60 | < 40 |
| hours_since_last_service | < 200h | 200–350h | > 350h |

## Known Anomalous Assets
- **AH04** (TAIL-AH04): vibration 8.2 mm/s → RED rotor
- **UH03** (TAIL-UH03): engine temp 228°C → RED engine
- **AW02** (TAIL-AW02): oil quality 32 → RED engine
- **MB03** (TAIL-MB03): 387h since service → RED drivetrain
- **CH04** (TAIL-CH04): vibration 5.8 + temp 198°C → dual AMBER

## Backend Setup (if not running)
```bash
# SQLite (no PostgreSQL needed)
cd /path/to/repo
PYTHONPATH=. DATABASE_URL=sqlite:///./mission_readiness.db python src/backend/db_init.py
PYTHONPATH=. DATABASE_URL=sqlite:///./mission_readiness.db uvicorn src.backend.main:app --port 8000

# Or with Docker Compose
docker-compose up --build
```
