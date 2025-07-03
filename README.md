💼 DealAgent007: M&A Research Assistant

 

DealAgent007 is an AI‑powered Mergers & Acquisitions research assistant, engineered to streamline due diligence, market analysis, valuation guidance, and risk assessment for target businesses—especially in the pet services sector (pet daycares, boarding centers, veterinary clinics, grooming, training, etc.).

🌐 Live Demo

Access the hosted API on Render (no CORS hassles):https://dealagent007.onrender.com

Interact with multiple agents by changing the path (/invoke, /stream, or /{agent_id}/invoke).

🚀 Key Features

Target Screening: Flag acquisition candidates (green/yellow/red) based on financial thresholds, operational metrics, and reputational signals.

Market Intelligence: Automated web searches for competitors, demand trends (boarding, daycare, grooming), partnership opportunities (local vets), and regulatory requirements (licenses, fire inspections, backflow testing).

Valuation Support: Revenue-multiple estimates, DVM‑count benchmarks, and customizable investment criteria (e.g. minimum $800k annual revenue for pet centers, $5M for veterinary practices).

Risk Assessment: Integrates flood history & disaster links via web search, plus optional real-time weather forecasts.

Streaming UI: Real-time “Thinking…” indicator in React, showing partial tokens as the model responds.

Multi-Agent Architecture: Plug in specialized agents (e.g. research_assistant, sop_creator) under one FastAPI service.

Secure & Extensible: Header-based bearer auth, pluggable tools (web search, calculator, weather), and Langfuse/LangSmith tracing support.

🛠️ Tech Stack

Agent Framework: LangGraph (stateful flows, tool chaining) + LangChain

Backend: FastAPI (streaming and non-streaming endpoints)

Frontend: React + Tailwind CSS

DevOps: Render (host API), Node.js for build, uv sync for Python env

⚙️ Setup & Local Development

1. Clone & Env

git clone https://github.com/jesseboudreau80/DealAgent007.git
cd DealAgent007
cp .env.example .env  # populate API keys: OPENAI_API_KEY, AUTH_SECRET, SERPAPI_API_KEY, OPENWEATHERMAP_API_KEY

2. Frontend (React)

cd chat-ui
npm install
# For local dev with hot reload:
npm start
# For production build:
npm run build
cd ..

3. Backend (FastAPI)

# Create & sync Python venv via uv (or poetry locally):
uv sync --frozen
source .venv/bin/activate
# Run service:
uv run-service      # or: python src/run_service.py

4. Streamlit Interface (Optional)

streamlit run src/streamlit_app.py

Your FastAPI docs will be live at http://localhost:8080/docs.

📝 Contributing & Roadmap

We’re building out specialized agents:

Research Assistant (M&A flows) — complete.

SOP Creator — draft in progress.

Financial Modeler — upcoming.

Contributions welcome!Please open issues or PRs against this repo.

📜 License

This project is MIT‑licensed. See the LICENSE file for details.

