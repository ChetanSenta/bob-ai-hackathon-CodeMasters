# How to Run This Submission

## Repository

https://github.com/ChetanSenta/bob-ai-hackathon-CodeMasters

**Team:** CodeMasters  
**Track:** AI  
**Lead:** Chetan Senta  

---

## Quickest path (Docker — recommended)

```bash
git clone https://github.com/ChetanSenta/bob-ai-hackathon-CodeMasters.git
cd bob-ai-hackathon-CodeMasters
cp .env.example .env
docker compose up --build
```

Open http://localhost:3000 — fleet readiness dashboard loads with 25 pre-seeded assets.

---

## No-Docker path (SQLite, works offline)

```bash
# 1. Build the IBM Bob MCP server (one-time)
cd src/mcp && npm install && npm run build && cd ../..

# 2. Start the backend
pip install -r src/backend/requirements.txt
PYTHONPATH=. DATABASE_URL=sqlite:///./mission_readiness.db python src/backend/db_init.py
PYTHONPATH=. DATABASE_URL=sqlite:///./mission_readiness.db uvicorn src.backend.main:app --port 8000

# 3. Start the frontend (new terminal)
cd src/frontend && npm install && npm run dev
```

Open http://localhost:3000.

---

## IBM Bob integration

1. Open this repo folder in IBM Bob
2. Bob auto-connects the `mission-readiness` MCP server (registered in `.bob/mcp.json`)
3. Select **🛡️ Mission Readiness Officer** from the mode dropdown
4. Ask: *"Is the fleet ready for tomorrow's mission?"*

Full instructions: `docs/bob-integration.md`

---

## Submission checklist

- [x] `submission.yaml` — all required fields filled (team: Chetan Senta, track: AI)
- [x] `README.md` — no placeholder text remaining
- [x] `docs/setup-guide.md` — exact tested commands to run the project
- [x] `src/` — full source code committed (backend + frontend + MCP server + dataset)
- [x] `demo/demo-video-link.txt` — demo walkthrough steps documented
- [x] `demo/live-demo-url.txt` — "NOT DEPLOYED" with local run instructions
- [x] `demo/screenshots/` — 6 screenshots (00–05) of the live running application
- [x] GitHub Actions **✅ Validate Submission** — green (Run #4)
- [x] Repository is **Public**
