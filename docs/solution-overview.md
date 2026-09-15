# Solution Overview

## What We Built

The **Mission Readiness Officer** is an IBM Bob Copilot backed by a FastAPI rules engine and a React dashboard. It gives military maintenance teams a single interface for three things that currently require three separate systems and hours of manual work:

1. **See** — which assets are ready and which are not (fleet dashboard)
2. **Understand** — why a specific asset is non-ready and what is actually wrong (per-asset detail with watsonx.ai explanation)
3. **Act** — what to fix first, in what order, before the next mission window (prioritised maintenance plan)

All three are accessible conversationally through IBM Bob, and all three are backed by the same live data.

---

## Core Mechanism

### 1. Data Ingestion
A maintenance technician uploads HUMS sensor exports (CSV) and service records through the React dashboard. The `/ingest/sensors` and `/ingest/service-records` FastAPI endpoints parse and store the data in PostgreSQL (or SQLite for offline use). No pre-processing is required — the system accepts the raw column format directly from HUMS exports.

**Dataset included in the repo:** `src/data/sample_hums_sensors.csv` — 600 sensor readings across 25 assets over 7 days, with deliberate anomalies injected into 5 assets to demonstrate failure detection.

### 2. Rules Engine Scoring (`src/backend/rules_engine.py`)
The rules engine evaluates each asset's most recent reading for each of the four sensor metrics:

| Metric | GREEN | AMBER | RED |
|--------|-------|-------|-----|
| `vibration_mm_s` | < 4.0 | 4.0–7.0 | > 7.0 |
| `engine_temp_c` | < 180°C | 180–220°C | > 220°C |
| `oil_quality_index` | > 60 | 40–60 | < 40 |
| `hours_since_last_service` | < 200h | 200–350h | > 350h |

Each component receives a numeric risk score (0–100) scaled linearly within its threshold band, plus a status (GREEN/AMBER/RED). An asset's overall status is the worst component status it holds.

### 3. Readiness API
Four FastAPI endpoints expose the scored data:
- `GET /readiness/fleet` — all 25 assets with status, score, and component breakdown
- `GET /readiness/asset/{asset_id}` — single asset detail with explanation
- `GET /predict/failures` — AMBER/RED components ranked CRITICAL/HIGH/MEDIUM by (score × mission proximity)
- `GET /maintenance/plan` — prioritised work orders with estimated duration and deadline

### 4. IBM Bob Tool-Calling via MCP
Bob is configured in `.bob/` using three files that IBM Bob actually reads:

- **`.bob/custom_modes.yaml`** — defines the `🛡️ Mission Readiness Officer` custom mode: persona, military-professional tone, tool usage rules, and the `mcp` tool group
- **`.bob/mcp.json`** — registers the Node.js MCP server (`src/mcp/`) so Bob auto-connects when the workspace opens
- **`.bob/rules/mission-readiness.md`** — injects domain context (thresholds, asset list, backend commands) into every conversation

The MCP server (`src/mcp/src/index.ts`) is a stdio process that Bob spawns as a child. It registers four typed MCP tools with Zod input schemas and proxies HTTP GET requests to the FastAPI backend. When Bob calls `get_asset_detail` with `asset_id=AH04`, the MCP server makes `GET /readiness/asset/AH04`, returns the JSON, and Bob synthesises a natural-language response.

### 5. watsonx.ai Explanation Layer (`src/backend/watsonx_client.py`)
When `WATSONX_API_KEY` is set, the `generate_explanation()` function calls the watsonx.ai inference API (`ibm/granite-13b-chat-v2`) with a structured prompt containing the asset's component readings, threshold values, and service history. The model returns a plain-English assessment suitable for a non-specialist crew chief. Without the API key the function returns a structured template string — the rest of the system is fully functional either way.

---

## What Makes This Different From a Naive Dashboard

A dashboard that shows sensor readings with colour codes is not new. The differentiating elements here are:

**Mission-window awareness.** Failure predictions are not just "this reading is high" — they are ranked by how many hours remain before each asset's next assigned mission window. A component at 6.9 mm/s vibration (AMBER) on an asset whose mission window is 4 hours away is more urgent than a RED component on an asset whose window is 5 days out.

**IBM Bob as the primary interface, not a bolt-on.** The four MCP tools are the only way to query live fleet data conversationally. Bob is not a chatbot wrapper around the dashboard — it is the readiness interrogation layer. A crew chief can ask *"Why is TAIL-AH04 grounded?"* and receive a grounded, data-backed answer citing exact metric values, the relevant threshold, and the specific repair recommendation, in seconds.

**Honest fallback.** The system declares what it knows and what it doesn't. If watsonx.ai is not configured, explanations say so. If an asset has no recent sensor readings, the API returns empty components rather than fabricating scores. Bob's mode instructions explicitly prohibit it from speculating without tool data.

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Readiness scoring | Rule-based thresholds | Demo-reproducible, fully explainable to judges, zero training data required. Thresholds are a single Python dict that can be tuned in minutes. |
| LLM use | Explanation generation only | AI is used where it adds value (natural language) and kept away from the decision logic (scoring). This makes the system auditable and trustworthy. |
| Bob integration | Custom mode + real MCP server | Uses IBM Bob's actual configuration formats (`.bob/custom_modes.yaml`, `.bob/mcp.json`) — not a fictional API. Bob is genuinely load-bearing. |
| Sensor ingest | CSV upload | Mirrors how HUMS exports are actually distributed in military operations. Works fully offline. |
| Database | PostgreSQL (SQLite fallback) | Production-credible ORM; SQLite fallback means judges can run the full stack without Docker or a database server. |
| Containerisation | Docker Compose | One command reproduces the full three-service stack. Build context set to repo root to preserve the `src.backend.*` package structure inside the container. |

---

## IBM Technologies Used

### IBM Bob
Configured as the Mission Readiness Officer via `.bob/custom_modes.yaml` (custom mode), `.bob/mcp.json` (MCP server registration), and `.bob/rules/mission-readiness.md` (domain rules). Bob uses MCP tool-calling — backed by a real Node.js stdio server — to query four live FastAPI endpoints during a conversation. This is the primary decision-support interface: all conversational readiness queries go through Bob.

### watsonx.ai
Used via the REST inference API (`src/backend/watsonx_client.py`) to generate natural-language maintenance explanations. The model (`ibm/granite-13b-chat-v2`) receives a structured JSON payload containing component name, current metric value, threshold, status, and recent reading history, and returns a plain-English assessment. Graceful fallback to template text when no API key is configured.

---

## User Experience Walkthrough

1. Analyst opens the workspace in IBM Bob and selects **🛡️ Mission Readiness Officer** mode
2. Asks: *"Is the fleet ready for tomorrow?"* — Bob calls `get_fleet_readiness`, returns counts and highlights RED assets
3. Asks: *"Why is TAIL-AH04 grounded?"* — Bob calls `get_asset_detail` with `asset_id=AH04`, returns component breakdown and watsonx.ai explanation
4. Asks: *"What will fail first before 0600Z?"* — Bob calls `get_failure_predictions`, ranks by CRITICAL urgency
5. Asks: *"Give me today's work orders"* — Bob calls `get_maintenance_plan`, returns prioritised task list with durations and deadlines
6. Analyst opens the React dashboard at `http://localhost:3000` for a visual overview of the full fleet grid and per-asset component detail pages
