# RegFlow AI

AI-native financial services platform — agentic compliance research, automated data analysis, and ML model monitoring.

## What Is This?

RegFlow AI is a full-stack platform with three integrated capabilities:

1. **Agentic Compliance Research Engine** — Multi-agent system where specialized AI agents collaborate to research regulatory documents, retrieve from RAG + GraphRAG, and produce structured reports with citations.

2. **Data Analysis Agent** — AI agent that performs automated analysis on financial datasets: loads data, cleans, runs statistics, detects anomalies, generates visualizations, and produces insight reports.

3. **Model Monitoring Dashboard** — Embedded credit risk model with real-time monitoring, drift detection, and automated retraining.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | TypeScript, Next.js, Tailwind CSS |
| Backend | Python, FastAPI, PostgreSQL, ChromaDB |
| AI/Agents | LangGraph, Pydantic AI, MCP, Azure OpenAI |
| ML/MLOps | XGBoost, scikit-learn, MLflow, Prometheus, Grafana |
| Security | OWASP Agentic AI Top 10, input validation, PII redaction, audit logging |
| Infrastructure | Docker, GitHub Actions CI/CD, Azure Container Apps |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/Faranmo/regflow-ai.git
cd regflow-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your values

# Start services (PostgreSQL + ChromaDB)
docker compose up -d

# Run the API
uvicorn src.api.main:app --reload
```

## Project Status

🚧 **Currently in Phase 1: Foundation**

See [docs/build-diary/](docs/build-diary/) for session-by-session progress.

## Documentation

- [Security Plan](docs/security-plan.md) — Full security approach and implementation roadmap
- [Build Diary](docs/build-diary/) — Session logs documenting what was built and learned

## License

MIT
