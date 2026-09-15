# Mission Readiness & Predictive Maintenance Copilot

> An IBM Bob Copilot that helps military maintenance teams predict component failures before the next mission window and act on them — through a conversational interface backed by live sensor data.

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | CodeMasters |
| **Track** | AI |
| **Team Lead** | Chetan Senta |
| **Members** | Chetan Senta |

---

## 🎯 Problem Statement

Military maintenance teams operate on fixed-schedule servicing cycles that ignore real-time platform health, leaving HUMS (Health & Usage Monitoring System) sensor data from engines, rotors, and hydraulics sitting unanalysed. Unexpected component failures cause unplanned groundings that contribute to the US military's $90B/year maintenance spend and directly reduce operational readiness when mission windows are tight.

---

## 💡 Solution

The **Mission Readiness Officer** is an IBM Bob Copilot backed by a FastAPI rules engine that ingests HUMS sensor telemetry via CSV upload, scores every component against configurable thresholds, and predicts which assets will fail before their next mission window. Maintenance crews converse naturally with Bob to query fleet status, understand failure risks, and receive a prioritised maintenance plan — with every recommendation explained in plain language by watsonx.ai.

---

## ✨ Key Features

- **Fleet Readiness Dashboard:** Real-time GREEN/AMBER/RED asset status grid with per-component breakdown
- **HUMS Data Ingestion:** CSV upload for sensor readings (vibration, engine temp, oil quality, hours-since-service) and service records
- **Failure Prediction Engine:** Rules-based component risk scoring ranked by urgency and mission proximity
- **IBM Bob Mission Readiness Officer:** Conversational copilot with tool-calling to live backend endpoints for fleet queries, asset details, failure predictions, and maintenance plans
- **watsonx.ai Explanations:** Natural-language maintenance recommendations generated for every AMBER/RED readiness issue

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python, TypeScript |
| **Frameworks** | FastAPI, React, SQLAlchemy, Vite, Tailwind CSS |
| **IBM Technologies** | IBM Bob, watsonx.ai |
| **Databases** | PostgreSQL |
| **Other** | Docker, Docker Compose, GitHub Actions |

---

## 📁 Repository Structure

```
├── src/
│   ├── backend/          # FastAPI application, rules engine, watsonx.ai client
│   ├── data/             # Synthetic HUMS sensor dataset and asset registry
│   └── frontend/         # React + Vite + Tailwind dashboard
├── docs/
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   ├── setup-guide.md
│   └── bob-integration.md
├── demo/
│   ├── screenshots/      # App screenshots
│   └── demo-video-link.txt
├── presentation/
├── .bob/                 # IBM Bob copilot configuration
├── docker-compose.yml
└── submission.yaml
```

---

## ⚡ How to Run

Full instructions are in [`docs/setup-guide.md`](docs/setup-guide.md). Quick start:

### Option A — Docker Compose (recommended, no Python/Node required)

```bash
git clone <this-repo-url>
cd bob-ai-hackathon-CodeMasters
cp .env.example .env          # optionally add WATSONX_API_KEY for live LLM explanations
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Option B — No Docker (SQLite, works offline)

```bash
# Build the Bob MCP server (one-time)
cd src/mcp && npm install && npm run build && cd ../..

# Backend (SQLite — no Postgres needed)
pip install -r src/backend/requirements.txt
PYTHONPATH=. DATABASE_URL=sqlite:///./mission_readiness.db python src/backend/db_init.py
PYTHONPATH=. DATABASE_URL=sqlite:///./mission_readiness.db uvicorn src.backend.main:app --port 8000

# Frontend (separate terminal)
cd src/frontend && npm install && npm run dev
```

---

## 🤖 IBM Bob Integration

Bob is configured via three files in `.bob/`:

| File | Purpose |
|---|---|
| `.bob/custom_modes.yaml` | Defines the **🛡️ Mission Readiness Officer** custom mode — persona, instructions, tool rules |
| `.bob/mcp.json` | Registers the MCP server (`src/mcp/`) — Bob auto-connects when the workspace opens |
| `.bob/rules/mission-readiness.md` | Domain context injected into every conversation |

When Bob is in **🛡️ Mission Readiness Officer** mode it calls four MCP tools backed by live FastAPI endpoints:

| Bob MCP Tool | Backend Endpoint | Purpose |
|---|---|---|
| `get_fleet_readiness` | `GET /readiness/fleet` | All assets with GREEN/AMBER/RED status |
| `get_asset_detail` | `GET /readiness/asset/{id}` | Per-component breakdown for one asset |
| `get_failure_predictions` | `GET /predict/failures` | Components at risk before next mission window |
| `get_maintenance_plan` | `GET /maintenance/plan` | Prioritised task list sorted by urgency |

**To activate:** build the MCP server (`cd src/mcp && npm install && npm run build`), open this workspace in Bob, and select **🛡️ Mission Readiness Officer** from the mode dropdown. See [`docs/bob-integration.md`](docs/bob-integration.md) for full setup steps.

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/](presentation/) |

---

## ⚠️ Known Limitations

- **Synthetic dataset** — sensor readings are generated, not sourced from real HUMS hardware
- **Rule-based scoring** — thresholds are hand-tuned constants, not a trained ML model; edge-case sensor patterns may be mis-classified
- **watsonx.ai is optional** — without a valid `WATSONX_API_KEY` the explanation field falls back to structured template text; the dashboard and Bob chat still work fully
- **Single-node deployment** — no horizontal scaling or auth layer; designed for demo, not production

---

## 🏅 What We're Most Proud Of

IBM Bob is the primary mission interface — not a cosmetic add-on. The integration uses a real Node.js MCP server (`src/mcp/`) that Bob spawns as a child process, calling four typed MCP tools that proxy live HTTP requests to the FastAPI backend. Bob synthesises the JSON responses into concise military-style briefings. Remove Bob and analysts have only the dashboard; the conversational readiness interrogation — *"Why is TAIL-AH04 grounded?"*, *"What will fail first?"*, *"Give me today's work orders"* — disappears entirely.

---
