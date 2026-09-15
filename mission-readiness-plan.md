# Mission Readiness & Predictive Maintenance — Bob Copilot

## Top-Level Overview

Build a Bob Copilot called **"Mission Readiness Officer"** that enables military maintenance teams to:

1. **Ingest** HUMS (Health & Usage Monitoring System) sensor data and service records via file upload
2. **Identify** non-ready assets using a component threshold rules engine
3. **Explain** each readiness issue in plain military language via watsonx.ai
4. **Predict** which components are at risk of failing before the next mission window
5. **Recommend** a prioritised, actionable maintenance plan

**Tech Stack:** Python/FastAPI (backend) · React (frontend) · PostgreSQL (data) · IBM watsonx.ai (LLM) · IBM Bob REST API (copilot)

**IBM Bob Role:** Primary conversational interface. Bob acts as the Mission Readiness Officer — users chat with Bob to query asset status, understand failure risks, and receive maintenance recommendations. Bob uses tool-calling to the FastAPI backend for all data operations.

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffold & Submission Metadata

**Status:** `[ ] pending`

**Intent:**  
Establish the full repository structure, fill all required `submission.yaml` fields, and update template documentation so GitHub Actions validation passes from the start.

**Expected Outcomes:**
- GitHub Actions `validate.yml` passes ✅ (green) on every push
- `submission.yaml` has no empty required fields
- `README.md` has no placeholder text
- `src/` directory contains at least one real file

**Todo List:**
1. Fill `submission.yaml` with team info, problem statement, solution summary, key features, and tech stack (`Python`, `TypeScript`, `FastAPI`, `React`, `PostgreSQL`, `watsonx.ai`, `IBM Bob`)
2. Update `README.md` with project title, team name, problem description, solution description, and how-to-run instructions
3. Update `docs/problem-statement.md` with the mission readiness / HUMS domain context
4. Update `docs/solution-overview.md` describing the Copilot architecture and data flow
5. Update `docs/architecture.md` with a Mermaid component diagram
6. Create a minimal `src/backend/__init__.py` (placeholder Python file) so `src/` passes the source code check
7. Update `docs/setup-guide.md` with exact steps to run the project locally

**Relevant Context:**
- [`submission.yaml`](submission.yaml) — evaluated by the CI validation pipeline
- [`.github/workflows/validate.yml`](.github/workflows/validate.yml) — lists every required field and file
- [`docs/template-guide.md`](docs/template-guide.md) — evaluation rubric and common mistakes

---

### Sub-Task 2 — Simulated HUMS Dataset

**Status:** `[ ] pending`

**Intent:**  
Create a realistic synthetic dataset that the demo can use without any external data dependency. The dataset simulates sensor telemetry and maintenance logs for a small fleet of military aircraft.

**Expected Outcomes:**
- `src/data/sample_hums_sensors.csv` — rows of sensor readings per asset per timestamp
- `src/data/sample_service_records.csv` — maintenance history per asset/component
- `src/data/asset_registry.json` — list of assets with type, tail number, next mission window
- Column definitions documented in `src/data/README.md`

**Todo List:**
1. Design the `sensors` schema: columns = `asset_id`, `tail_number`, `timestamp`, `component` (engine, rotor, hydraulics, avionics, landing_gear), `metric_name` (vibration_hz, temp_c, pressure_bar, oil_level_pct, cycles_since_overhaul), `value`, `unit`
2. Design the `service_records` schema: columns = `record_id`, `asset_id`, `component`, `maintenance_type`, `technician`, `date`, `notes`, `hours_flown_since`
3. Generate ~500 sensor rows covering 8 assets: 4 Apache AH-64, 2 CH-47 Chinook, 2 M1 Abrams (mixed readiness — some healthy, some with anomalies)
4. Inject deliberate anomalies: 2 assets with vibration above threshold, 1 with high oil temp, 1 with cycles near overhaul limit
5. Generate ~40 service record rows across the fleet
6. Create `src/data/asset_registry.json` with next mission window dates
7. Write `src/data/README.md` documenting schema and anomaly injection rationale

**Relevant Context:**
- `src/` — target directory (currently only contains `README.md` and `.env.example`)
- `.gitignore` excludes `data/` at root level — dataset lives inside `src/data/` to remain tracked

---

### Sub-Task 3 — FastAPI Backend

**Status:** `[ ] pending`

**Intent:**  
Build the Python/FastAPI service that handles sensor data ingestion, runs the rules-based readiness scoring engine, and exposes tool-callable endpoints that Bob will call during conversations.

**Expected Outcomes:**
- FastAPI app running on `localhost:8000`
- Endpoints: data upload, fleet readiness summary, per-asset detail, component risk scores, maintenance plan
- PostgreSQL database with `assets`, `sensor_readings`, and `service_records` tables
- Rules engine that scores each component as GREEN / AMBER / RED based on configurable thresholds
- `requirements.txt` listing all Python dependencies

**Todo List:**
1. Create `src/backend/main.py` — FastAPI app entry point with CORS enabled for React frontend
2. Create `src/backend/database.py` — SQLAlchemy engine + session factory using `DATABASE_URL` from `.env`
3. Create `src/backend/models.py` — SQLAlchemy ORM models: `Asset`, `SensorReading`, `ServiceRecord`
4. Create `src/backend/schemas.py` — Pydantic request/response models for all endpoints
5. Create `src/backend/routers/ingest.py` — `POST /ingest/sensors` and `POST /ingest/service-records` accepting CSV/JSON upload, parsing and storing to PostgreSQL
6. Create `src/backend/routers/readiness.py` — `GET /readiness/fleet` (all assets with status), `GET /readiness/asset/{asset_id}` (detailed component breakdown)
7. Create `src/backend/routers/predictions.py` — `GET /predict/failures` returning components at risk before the next mission window, ranked by urgency
8. Create `src/backend/routers/maintenance.py` — `GET /maintenance/plan` returning prioritised task list (sorted by risk level + mission proximity)
9. Create `src/backend/rules_engine.py` — threshold table per component/metric, scoring logic returning GREEN/AMBER/RED + score (0–100), time-to-failure estimate
10. Create `src/backend/watsonx_client.py` — wrapper around watsonx.ai REST API to generate natural-language explanations given a structured readiness payload
11. Create `src/backend/alembic/` — database migration setup (or a `db_init.py` script for simpler demo setup)
12. Create `requirements.txt` at `src/backend/requirements.txt`
13. Update `src/backend/.env.example` with all required environment variables
14. Smoke-test all endpoints manually against the sample dataset

**Relevant Context:**
- `.env.example` at repo root shows `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL`, `DATABASE_URL`
- Sub-Task 2 defines the data schema this backend must consume
- Sub-Task 5 (Bob integration) will call these endpoints as tools — keep response payloads JSON-serialisable and concise

---

### Sub-Task 4 — React Frontend Dashboard

**Status:** `[ ] pending`

**Intent:**  
Build a React dashboard that lets analysts upload sensor data, view fleet readiness at a glance, and drill into individual asset details. The dashboard complements the Bob chat interface with a visual overview.

**Expected Outcomes:**
- React app running on `localhost:3000`
- Fleet overview page: grid of asset cards with GREEN/AMBER/RED status badges
- Asset detail page: per-component status breakdown, recent sensor readings, service history
- File upload UI: drag-and-drop CSV/JSON upload for sensors and service records
- Maintenance plan page: prioritised task list sorted by urgency
- Responsive layout (desktop-first)

**Todo List:**
1. Scaffold React app in `src/frontend/` using Vite + TypeScript (`npm create vite@latest`)
2. Install dependencies: `axios`, `react-router-dom`, `tailwindcss`, a charting library (e.g. `recharts`)
3. Create `src/frontend/src/api/client.ts` — typed axios wrapper pointing to `http://localhost:8000`
4. Build `FleetOverview` page — fetches `GET /readiness/fleet` and renders asset status cards
5. Build `AssetDetail` page — fetches `GET /readiness/asset/{asset_id}`, shows component table and sensor trend mini-charts
6. Build `DataUpload` page — file input for sensors CSV and service records CSV, calls `POST /ingest/*` endpoints, shows success/error state
7. Build `MaintenancePlan` page — fetches `GET /maintenance/plan`, renders sorted task list with urgency chips (CRITICAL / HIGH / MEDIUM)
8. Add navigation bar with links to all four pages and a prominent "Chat with Bob" button (links to the Bob copilot)
9. Create `src/frontend/package.json` and `src/frontend/vite.config.ts`
10. Verify the UI loads sample data from the backend end-to-end

**Relevant Context:**
- Sub-Task 3 defines the backend endpoints this frontend consumes
- The "Chat with Bob" button links to the Bob copilot configured in Sub-Task 5
- `src/frontend/` directory does not yet exist

---

### Sub-Task 5 — IBM Bob Copilot Configuration

**Status:** `[ ] pending`

**Intent:**  
Configure the IBM Bob Copilot as the "Mission Readiness Officer" persona. Bob uses a military-domain system prompt and tool-calling to the FastAPI backend so analysts can converse naturally about readiness, failures, and maintenance priorities.

**Expected Outcomes:**
- `.bob/` directory with Bob copilot configuration files
- System prompt establishes the "Mission Readiness Officer" persona with military tone
- Bob tools registered for: fleet readiness query, asset detail query, failure predictions, maintenance plan
- Bob can answer questions like "Is Tail #7 ready for tomorrow?", "What will fail first?", "Give me today's maintenance priorities"
- `docs/bob-integration.md` documents the copilot setup and how to register it

**Todo List:**
1. Create `.bob/system-prompt.md` — Mission Readiness Officer persona: military tone, domain expertise framing, instructions to always cite component names and risk levels, escalate CRITICAL items, never speculate without data
2. Create `.bob/tools.yaml` — define four tools Bob can call:
   - `get_fleet_readiness` → `GET /readiness/fleet`
   - `get_asset_detail` → `GET /readiness/asset/{asset_id}` (param: `asset_id`)
   - `get_failure_predictions` → `GET /predict/failures`
   - `get_maintenance_plan` → `GET /maintenance/plan`
3. Create `.bob/bob.yaml` — top-level copilot config referencing the system prompt and tools, setting the model to `ibm/granite-13b-chat-v2` or `meta-llama/llama-3-70b-instruct` via watsonx.ai
4. Write `docs/bob-integration.md` — step-by-step instructions for registering the copilot with IBM Bob REST API, including required environment variables and the registration `curl` command
5. Create `src/bob/register_copilot.py` — Python script that calls the IBM Bob REST API to register/update the copilot programmatically (reads from `.bob/bob.yaml`)
6. Test Bob end-to-end: ask "Which assets are not mission-ready?" and verify Bob calls the tool, receives JSON, and returns a natural-language response

**Relevant Context:**
- IBM Bob REST API is the integration method (watsonx-backed assistant with tool-calling)
- `.env.example` already includes `WATSONX_API_KEY` and `WATSONX_PROJECT_ID`
- Sub-Task 3 backend endpoints are the tool targets — they must be running and accessible for Bob to call
- Scoring rubric: "IBM Bob must be load-bearing, not just name-dropped" (10 points)

---

### Sub-Task 6 — Demo Polish & Final Submission Artifacts

**Status:** `[x] done`

**Intent:**  
Complete all submission artifacts required by the hackathon validator, add screenshots, and ensure the full project runs end-to-end from a clean checkout so judges can reproduce the demo.

**Expected Outcomes:**
- `docs/setup-guide.md` has exact, tested commands to run the full stack
- `demo/screenshots/` contains at least 3 labelled screenshots
- `demo/demo-video-link.txt` has a valid video URL (YouTube/Loom)
- GitHub Actions validation passes ✅
- `docker-compose.yml` (optional but recommended) for one-command startup

**Todo List:**
1. Write `docker-compose.yml` at repo root: services for `db` (postgres:15), `backend` (FastAPI), `frontend` (Vite dev server) — wires up environment variables from `.env`
2. Update `docs/setup-guide.md` with two paths: (a) Docker Compose one-liner, (b) manual step-by-step
3. Run `docker-compose up` from a clean state and verify the full stack loads sample data and the UI shows fleet readiness
4. Take screenshots: (1) fleet overview dashboard, (2) asset detail with RED component, (3) Bob chat showing a maintenance recommendation
5. Add screenshots to `demo/screenshots/` following the naming convention in `demo/screenshots/README.md`
6. Record a 3–5 minute demo video: upload sensor data → view dashboard → chat with Bob → receive maintenance plan
7. Add video URL to `demo/demo-video-link.txt`
8. Verify GitHub Actions `validate.yml` passes all checks ✅
9. Final check: no placeholder text in `README.md`, no empty required fields in `submission.yaml`

**Relevant Context:**
- [`demo/screenshots/README.md`](demo/screenshots/README.md) — naming conventions for screenshots
- [`.github/workflows/validate.yml`](.github/workflows/validate.yml) — exact checks that must pass
- [`docs/template-guide.md`](docs/template-guide.md) — common mistakes section (pp. common pitfalls)

---

## Implementation Order

```
Sub-Task 1 (Scaffold)
    ↓
Sub-Task 2 (Dataset)
    ↓
Sub-Task 3 (Backend) ←→ Sub-Task 4 (Frontend)   [can run in parallel after ST2]
    ↓
Sub-Task 5 (Bob Copilot)                          [depends on ST3 endpoints]
    ↓
Sub-Task 6 (Demo & Submission)
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Readiness scoring | Rule-based thresholds | Demo-friendly, no model training required, explainable |
| LLM use | watsonx.ai for explanation generation only | Keeps AI meaningful without over-engineering |
| Bob integration | Tool-calling via REST API | Makes Bob load-bearing, not cosmetic |
| Data ingestion | CSV upload via UI | Simpler than live streaming, works fully offline |
| Frontend | React + Vite + Tailwind | Lightweight, fast to scaffold |
| DB | PostgreSQL | Matches `.env.example`, production-credible |
| Containerisation | Docker Compose | One-command reproducibility for judges |
