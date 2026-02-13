# AI Clinical Chatbot MVP

An AI-powered clinical chatbot for a HealthTech platform focused on mental health in Mexico (LATAM). Built with FastAPI + Next.js, featuring real-time SSE streaming, risk assessment, triage evaluation, and crisis resource management.

## Architecture

```
User → Frontend (Next.js 14) → SSE Stream → Backend (FastAPI)
                                                 │
                                                 ├── Risk Scorer (5-signal, 0-100)
                                                 ├── Triage Evaluator (4-rule cascade)
                                                 ├── LLM Orchestrator (mock/openai/anthropic)
                                                 ├── PII Anonymizer
                                                 └── Session Repository (thread-safe)
```

## Monorepo Structure

```
Health_AI_MVP/
├── backend/          # FastAPI Python backend
├── frontend/         # Next.js TypeScript frontend
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- Or: Python 3.11+ and Node.js 18+

### Using Docker (Recommended)

```bash
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

### Manual Setup

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
cd backend
pytest tests/ -v
```

## Documentation

- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | FastAPI, Pydantic v2, Python 3.11+  |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Streaming | Server-Sent Events (SSE)           |
| State    | Zustand                             |
| Testing  | pytest, pytest-asyncio              |

## License

Proprietary — All rights reserved.
