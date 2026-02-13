# Clinical Chatbot Backend

FastAPI backend for the AI Clinical Chatbot MVP. Provides real-time SSE streaming, risk assessment, triage evaluation, and session management.

## Tech Stack

| Component       | Technology              |
|-----------------|-------------------------|
| Framework       | FastAPI 0.110+          |
| Validation      | Pydantic v2             |
| Settings        | pydantic-settings       |
| Server          | Uvicorn                 |
| Testing         | pytest + pytest-asyncio |
| Python          | 3.11+                   |

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

```json
{"status": "healthy", "service": "AI Clinical Chatbot MVP", "version": "0.1.0", "active_sessions": 0}
```

### Send Message

```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_message": "I have been feeling stressed lately"}'
```

```json
{
  "session_id": "abc-123",
  "bot_response": "I hear you...",
  "risk_score": 15,
  "risk_level": "low",
  "triage_activated": false,
  "human_handoff": false,
  "crisis_resources": null,
  "session_message_count": 1,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Stream Message (SSE)

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"user_message": "I need someone to talk to"}'
```

SSE events:
- `metadata` — session info, risk score, triage status
- `crisis` — crisis resources (when applicable)
- `token` — streamed response word by word
- `done` — stream complete with message count

### Get History

```bash
curl http://localhost:8000/api/v1/chat/SESSION_ID/history
```

### Trigger Handoff

```bash
curl -X POST http://localhost:8000/api/v1/chat/SESSION_ID/handoff
```

## Conversation Flow Examples

### Normal Conversation

```bash
# First message — creates session
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Hello, I wanted to talk about how I am feeling"}'

# Continue conversation with session_id
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "user_message": "I have been feeling overwhelmed at work"}'
```

### High Risk Detection

```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_message": "I feel hopeless and I cant go on anymore"}'
# → triage_activated: true, human_handoff: true
```

### User Requests Professional

```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_message": "I want to talk to a real person"}'
# → human_handoff: true, handoff_reason: USER_REQUESTED
```

### Critical Risk with Crisis Resources

```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_message": "I want to end my life"}'
# → crisis_resources with emergency numbers
```

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                # FastAPI app factory with lifespan
│   ├── config.py              # Pydantic settings configuration
│   ├── exceptions.py          # Custom exception hierarchy
│   ├── dependencies.py        # FastAPI dependency injection
│   ├── models/
│   │   ├── enums.py           # RiskLevel, MessageRole, etc.
│   │   ├── schemas.py         # Pydantic v2 request/response models
│   │   └── session.py         # Session dataclass
│   ├── repositories/
│   │   ├── base.py            # Repository protocol (interface)
│   │   └── memory_session.py  # Thread-safe in-memory store
│   ├── services/
│   │   ├── risk_scorer.py     # 5-signal risk scoring engine
│   │   ├── triage_evaluator.py# Triage rules and handoff logic
│   │   ├── chatbot.py         # LLM orchestrator + validator
│   │   ├── anonymizer.py      # PII stripping before LLM
│   │   └── session_service.py # Session business logic
│   ├── routers/
│   │   ├── chat.py            # Chat endpoints + SSE streaming
│   │   └── health.py          # Health check endpoint
│   ├── data/
│   │   ├── risk_keywords.json # Weighted keywords by severity
│   │   └── crisis_resources.json # Mexico emergency resources
│   └── utils/
│       └── logging_config.py  # Structured logging setup
└── tests/
    ├── conftest.py            # Shared fixtures and factories
    ├── test_risk_scorer.py    # Risk scoring unit tests
    ├── test_triage_evaluator.py # Triage logic tests
    ├── test_chatbot.py        # Chatbot service tests
    ├── test_anonymizer.py     # PII anonymizer tests
    ├── test_session_service.py# Session management tests
    └── test_api_integration.py# API integration tests
```

## Configuration

All settings are configurable via environment variables. See `.env.example` for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `mock` | LLM backend: mock, openai, anthropic |
| `RISK_THRESHOLD_HIGH` | `60` | Score threshold for high risk |
| `RISK_THRESHOLD_CRITICAL` | `80` | Score threshold for critical risk |
| `SESSION_MAX_MESSAGES_BEFORE_CHECKIN` | `15` | Messages before check-in prompt |

## Design Decisions

- **Mock LLM by default**: Ships with pattern-based responses for development without API keys.
- **Repository pattern**: Storage is abstracted behind a protocol for easy swapping (memory → Redis → PostgreSQL).
- **Thread-safe sessions**: In-memory store uses `threading.Lock` for concurrent request safety.
- **5-signal risk scoring**: Combines keyword matching, sentiment analysis, behavioral signals, escalation detection, and session history.
- **PII anonymization**: All user messages are stripped of identifiable information before processing.
- **No PII in logs**: Only anonymized session IDs and numeric scores are logged.
