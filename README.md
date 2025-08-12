# 🕵️‍♂️ DealAgent007 – AI App Template (React + FastAPI)

A lightweight starter for building **AI-powered web apps** fast:
- **React** frontend
- **FastAPI** backend
- Pluggable **LLM agent(s)** with clean routing (OpenAI or local via AnythingLLM)

Use this to spin up internal tools, demos, and client-facing chat agents in minutes.

> This repo functions as a **Template**. Click **Use this template → Create a new repository** to start fresh.

---

## 🎯 Why this exists

- A repeatable scaffold for **React + FastAPI + Agent** apps  
- Opinionated patterns for **routing, env, and auth**  
- Clean separation of concerns so you can swap models or UI without redoing infra

---

## 🧱 What’s included (current)

- Frontend scaffold (React, Vite) with starter pages/components  
- FastAPI router with `/api/health` and agent endpoint stubs  
- `.env.example` with sensible variables  
- CORS + JSON error handling  
- Basic project structure and README you’re reading now 😄

---

## 🗺️ Roadmap (polish this template)

- [ ] Add `/api/agent/chat` endpoint with provider switch (OpenAI / AnythingLLM)  
- [ ] Add React chat widget and message history  
- [ ] Add `.devcontainer/` for GitHub Codespaces one-click start  
- [ ] Add Makefile or taskfile for one-command dev (`make dev`)  
- [ ] Add auth (JWT session) for protected routes  
- [ ] Add deploy recipes (Render / Fly.io)  

---

## 🛠️ Tech Stack

- **Frontend:** React + Vite (Planned: Tailwind)  
- **Backend:** FastAPI (Python 3.11+)  
- **AI Layer:** OpenAI API or AnythingLLM router (switchable)  
- **Tooling:** dotenv, CORS, requests/httpx  

---

## 📁 Structure (recommended)

frontend/
src/
components/
pages/
lib/
index.html
package.json
backend/
app/
routers/
agent.py # POST /api/agent/chat
health.py # GET /api/health
models.py
deps.py
config.py
main.py
.env.example
README.md

yaml
Copy
Edit

yaml


---

## ⚙️ Quick Start (Local)

### Backend
```bash
cd backend
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload


Frontend
bash
Copy
Edit
cd frontend
npm install
npm run dev
Visit:

API: http://localhost:8000/api/health

Web: http://localhost:5173

🔌 Configure AI Provider
In .env (backend):

OPENAI_API_KEY=your_key_here
# or, when using AnythingLLM router
ANYTHINGLLM_URL=http://localhost:3001
ANYTHINGLLM_API_KEY=your_router_key
AGENT_PROVIDER=openai     # or anythingllm


🔍 Example Workflow

[React UI] ──> [FastAPI /api/agent/chat] ──> [Provider: OpenAI | AnythingLLM]
       ^                                                  |
       |------------------ response + sources ------------|


🧪 Health Check

curl http://localhost:8000/api/health
# => {"status": "ok"}


📚 Notes
This is a template first and a demo second. It’s intentionally lean so you can fork/clone and move quickly.

🗺️ Future Plans
Cookie/session auth with role-based agent access

File upload + retrieval-augmented generation (RAG)

Deployment presets for Render (Docker) and Fly.io

Example agents: “Compliance Scout”, “Ops Coach”, “Marketing Buddy”

🪪 License
MIT

