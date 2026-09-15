# Setup Guide

> **This file is read by the automated evaluation pipeline. Be precise and complete.**

## Prerequisites

Before you begin, ensure you have the following installed:

- [ ] Python 3.11+
- [ ] Node.js 20+
- [ ] Docker Desktop (for Option A — Docker Compose)
- [ ] PostgreSQL 15+ running locally (for Option B — manual only)
- [ ] An IBM Cloud account with watsonx.ai access (for LLM explanation features)

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Description | Required |
|---|---|---|
| `WATSONX_API_KEY` | Your IBM Cloud API key with watsonx.ai access | Yes (LLM features) |
| `WATSONX_PROJECT_ID` | Your watsonx.ai project ID | Yes (LLM features) |
| `WATSONX_URL` | watsonx.ai endpoint (e.g. `https://us-south.ml.cloud.ibm.com`) | Yes (LLM features) |
| `BOB_API_KEY` | IBM Bob REST API key for Copilot registration | Yes (Bob features) |
| `BOB_API_URL` | IBM Bob instance URL | Yes (Bob features) |
| `DATABASE_URL` | PostgreSQL connection string — set automatically by Docker Compose | Manual setup only |

> **Note:** watsonx.ai and Bob variables are optional for the demo. The backend falls back to template-based explanations when no API key is provided, so the full dashboard works without IBM Cloud credentials.

---

## Option A — Docker Compose (recommended)

This is the fastest path. Docker Compose starts PostgreSQL, the FastAPI backend, and the React frontend with a single command.

```bash
# 1. Clone the repository
git clone https://github.com/codemasters/mission-readiness-officer.git
cd mission-readiness-officer

# 2. Configure environment
cp .env.example .env
# Open .env and fill in WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL
# DATABASE_URL is pre-configured for the Docker Compose postgres service

# 3. Build and start all services
docker compose up --build
```

Services started:

| Service | URL |
|---|---|
| React frontend | http://localhost:3000 |
| FastAPI backend | http://localhost:8000 |
| Interactive API docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 (internal only) |

To stop all services:

```bash
docker compose down
```

To reset the database (wipe all data):

```bash
docker compose down -v
docker compose up --build
```

---

## Option B — No Docker (SQLite, works fully offline)

This path requires Python 3.11+ and Node.js 20+. It uses SQLite instead of PostgreSQL — no database server needed.

> **Important:** All commands must be run from the **repository root**, not from `src/backend/`. The `PYTHONPATH=.` prefix and `DATABASE_URL` variable are required — do not omit them.

### 1. Build the Bob MCP server (one-time)

```bash
cd src/mcp
npm install
npm run build
cd ../..
```

Verify: `ls src/mcp/build/index.js` should show the compiled file.

### 2. Backend (FastAPI + SQLite)

```bash
# From the repo root:
pip install -r src/backend/requirements.txt

# Initialise database schema and seed sample data
PYTHONPATH=. DATABASE_URL=sqlite:///./mission_readiness.db python src/backend/db_init.py

# Start the API server
PYTHONPATH=. DATABASE_URL=sqlite:///./mission_readiness.db uvicorn src.backend.main:app --port 8000
```

The API is available at http://localhost:8000 and interactive docs at http://localhost:8000/docs.

Expected output from `db_init.py`:
```
Creating tables …
Tables created.
Seeding assets …
  25 assets seeded.
Seeding sensor readings …
  600 sensor readings seeded.
Seeding service records …
  65 service records seeded.
Database initialisation complete.
```

### 3. Frontend (React)

Open a new terminal (keep the backend running):

```bash
cd src/frontend
npm install
npm run dev
```

The dashboard is available at http://localhost:3000.

### 4. Verify the stack

```bash
# Should return JSON with 25 assets and summary counts
curl http://localhost:8000/readiness/fleet

# Should return 4-6 failure predictions (CRITICAL first)
curl http://localhost:8000/predict/failures
```

---

## IBM Bob Setup (after Option A or B)

```bash
# If you haven't built the MCP server yet:
cd src/mcp && npm install && npm run build && cd ../..

# Open this repo folder in IBM Bob
# Select 🛡️ Mission Readiness Officer from the mode dropdown
# The MCP server connects automatically — no manual registration needed
```

See [`docs/bob-integration.md`](bob-integration.md) for full instructions.

---

## Troubleshooting

### General issues

| Issue | Solution |
|---|---|
| `connection refused` on port 8000 | Ensure the FastAPI server is running. Check the terminal where you started `uvicorn`. |
| `connection refused` on port 5432 | If using Docker Compose, run `docker compose up db`. If using Option B, you don't need Postgres — use SQLite (see Option B above). |
| `ModuleNotFoundError: No module named 'src'` | You are missing `PYTHONPATH=.` — run all backend commands from the repo root with `PYTHONPATH=.` prefixed. |
| `ModuleNotFoundError: No module named 'fastapi'` | Run `pip install -r src/backend/requirements.txt` from the repo root. |
| React blank page | Ensure the backend is running on port 8000. Check browser console for CORS errors. |
| watsonx.ai `401 Unauthorized` | Check `WATSONX_API_KEY` in your `.env` — ensure it is a current IBM Cloud API key. Without it the system falls back to template explanations automatically. |
| MCP server not connecting in Bob | Run `ls src/mcp/build/index.js`. If missing, build it: `cd src/mcp && npm run build`. |

### Bugs encountered during development (documented for judges)

These are real bugs we hit and fixed — you may encounter them if you modify the backend.

| Bug | Symptom | Root Cause | Fix |
|-----|---------|------------|-----|
| `IndexError: 2` in `db_init.py` | Backend container crashes on startup | `Path(__file__).resolve().parents[2]` overruns the filesystem root when `db_init.py` is at `/app/db_init.py` inside Docker (only 2 parent levels exist) | Replaced with a guarded walk: check `_parent != _here` before accessing each level |
| `no such table: assets` after `create_all()` | Database tables created but immediately missing | `models.py` imported `Base` from `src.backend.database` while `db_init.py` imported `Base` from bare `database` — two different module objects, so `Asset` registered against one `Base` while `create_all()` ran on the other (empty) one | Added portable try/except import to `models.py` to match `db_init.py`'s import path |
| Docker build fails with `COPY ../../src/data` | `docker build` rejects the path | Docker build context was `src/backend/` — COPY paths cannot escape the build context | Changed `docker-compose.yml` build context to `.` (repo root) and updated Dockerfile to `COPY src/ ./src/` |
| `ModuleNotFoundError: No module named 'src'` | `uvicorn main:app` fails | Running from `src/backend/` without `PYTHONPATH` set — `src.backend.*` imports cannot resolve | Always run from repo root with `PYTHONPATH=. uvicorn src.backend.main:app` |
