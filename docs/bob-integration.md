# Bob Copilot Integration — Mission Readiness Officer

## 1. Overview

The **Mission Readiness Officer** is a custom IBM Bob mode backed by an MCP server. It gives military maintenance teams a conversational interface to the fleet readiness system. Bob is load-bearing: every answer it gives is backed by a live MCP tool call to the FastAPI backend, which queries real sensor data and applies the rules engine.

### How the integration works

```
User types question in Bob chat
        ↓
🛡️ Mission Readiness Officer mode
  (persona + instructions from .bob/custom_modes.yaml)
        ↓
Bob calls MCP tool via mission-readiness server
  (src/mcp/build/index.js — registered in .bob/mcp.json)
        ↓
MCP server proxies HTTP GET to FastAPI backend
  (http://localhost:8000)
        ↓
FastAPI queries PostgreSQL, runs rules engine
        ↓
JSON response → Bob synthesises natural-language reply
```

### IBM Bob configuration files

| File | Purpose |
|------|---------|
| `.bob/custom_modes.yaml` | Defines the 🛡️ Mission Readiness Officer mode (persona, tool rules, asset reference) |
| `.bob/mcp.json` | Registers the MCP server so Bob auto-connects on workspace open |
| `.bob/rules/mission-readiness.md` | Domain rules injected into every conversation (thresholds, asset list, backend setup) |

### MCP tools

| Tool | Endpoint | Purpose |
|------|----------|---------|
| `get_fleet_readiness` | `GET /readiness/fleet` | Fleet-wide RED/AMBER/GREEN summary |
| `get_asset_detail` | `GET /readiness/asset/{asset_id}` | Per-asset component breakdown |
| `get_failure_predictions` | `GET /predict/failures` | Ranked failure predictions |
| `get_maintenance_plan` | `GET /maintenance/plan` | Prioritised work orders |

---

## 2. Prerequisites

- **IBM Bob** installed (IDE or Shell edition)
- **Node.js 20+** — to run the MCP server
- **FastAPI backend running** on `http://localhost:8000` (see step 3)

---

## 3. Setup

### Step 1 — Build the MCP server

```bash
cd src/mcp
npm install
npm run build
```

This compiles `src/index.ts` → `build/index.js`. The file is set executable automatically.

### Step 2 — Start the FastAPI backend

**Option A — Docker Compose (recommended)**
```bash
cp .env.example .env          # optionally add WATSONX_API_KEY for live LLM explanations
docker-compose up --build
```

**Option B — Local (SQLite, no PostgreSQL needed)**
```bash
pip install -r src/backend/requirements.txt
PYTHONPATH=. DATABASE_URL=sqlite:///./mission_readiness.db python src/backend/db_init.py
PYTHONPATH=. DATABASE_URL=sqlite:///./mission_readiness.db uvicorn src.backend.main:app --port 8000
```

Verify it works:
```bash
curl http://localhost:8000/readiness/fleet
# Should return JSON with 25 assets
```

### Step 3 — Open the workspace in Bob

1. Open the `bob-ai-hackathon-CodeMasters/` folder in Bob.
2. Bob automatically reads `.bob/mcp.json` and connects the `mission-readiness` MCP server.
3. You should see **mission-readiness** appear as a connected server in Bob's MCP panel.

### Step 4 — Switch to Mission Readiness Officer mode

1. Click the **mode selector** dropdown in the Bob chat input area.
2. Select **🛡️ Mission Readiness Officer**.
3. Start chatting.

---

## 4. Sample conversations

### Fleet status
> **You:** Is the fleet ready for tomorrow's mission?

Bob calls `get_fleet_readiness` → returns 25 assets → replies:

> **Bob:** Fleet status as of now: **4 assets are RED — mission-blocked.**
> - TAIL-AH04 (Apache): rotor vibration CRITICAL at 8.2 mm/s (threshold 7.0)
> - TAIL-UH03 (Black Hawk): engine temperature CRITICAL at 228°C (threshold 220°C)
> - TAIL-AW02 (A-10): oil quality index CRITICAL at 32 (threshold 40)
> - TAIL-MB03 (M1 Abrams): 387 hours since last service (threshold 350h)
>
> 1 asset AMBER (CH04 — dual trending). 20 assets GREEN and mission-ready.

### Single asset diagnosis
> **You:** Why is TAIL-AH04 grounded?

Bob calls `get_asset_detail` with `asset_id=AH04` → replies:

> **Bob:** TAIL-AH04 (AH-64 Apache) — **STATUS: RED. Mission-blocked.**
> Root cause: main rotor vibration at 8.2 mm/s exceeds the RED threshold of 7.0 mm/s.
> Probable cause: rotor imbalance or bearing wear. Last serviced within overhaul window.
> Immediate action: rotor balance inspection and dynamic balancing required before return to service.

### Failure predictions
> **You:** What's going to fail first?

Bob calls `get_failure_predictions` → replies with CRITICAL items first.

### Maintenance plan
> **You:** Give me today's work orders.

Bob calls `get_maintenance_plan` → returns prioritised task list.

---

## 5. Troubleshooting

### MCP server not connecting

Check Bob's MCP panel — if `mission-readiness` shows as disconnected:

1. Verify the build exists: `ls src/mcp/build/index.js`
2. If missing, rebuild: `cd src/mcp && npm run build`
3. Verify Node.js is available: `node --version` (must be 20+)
4. Check `.bob/mcp.json` — the `args` path must resolve to the built file

### Tool call returns "Cannot reach backend"

The MCP server cannot connect to `http://localhost:8000`. Start the backend:
```bash
curl http://localhost:8000/readiness/fleet   # test if it's up
```
If Docker: `docker-compose up` from the repo root.

### Bob answers without calling a tool

Switch to **🛡️ Mission Readiness Officer** mode — other modes do not have the fleet domain instructions. The tool-calling rules only apply in that mode.

### Custom mode not appearing in mode selector

Verify `.bob/custom_modes.yaml` exists at the repo root and is valid YAML:
```bash
python -c "import yaml; yaml.safe_load(open('.bob/custom_modes.yaml')); print('OK')"
```
Then reload Bob (close and reopen the workspace).

---

## 6. Files reference

```
.bob/
├── custom_modes.yaml          # 🛡️ Mission Readiness Officer mode definition
├── mcp.json                   # MCP server registration (auto-connects on workspace open)
├── rules/
│   └── mission-readiness.md   # Domain rules injected into every conversation
├── bob.yaml                   # Legacy registration script config (not used by Bob directly)
├── system-prompt.md           # Source text for the mode's roleDefinition
└── tools.yaml                 # Source tool descriptions (incorporated into custom_modes.yaml)

src/mcp/
├── src/index.ts               # MCP server source (TypeScript)
├── build/index.js             # Compiled server — what Bob spawns
├── package.json
└── tsconfig.json

src/bob/
└── register_copilot.py        # Legacy script (not required for Bob IDE/Shell integration)
```
