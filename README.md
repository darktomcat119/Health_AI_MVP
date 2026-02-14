# Health AI MVP -- Mental Health Clinical Chatbot

AI-powered mental health support chatbot MVP for a HealthTech platform in Mexico. Built with FastAPI + Next.js, featuring real-time streaming, risk scoring, triage with human handoff, and privacy-first design. The LLM provider is cloud-based and provider-agnostic (OpenAI by default, easily swappable).

## Architecture

```
Browser (Next.js 14) --SSE streaming--> Next.js Server --HTTP--> FastAPI Backend
                                        (API rewrites)            |
                                                                  +-- PII Anonymizer
                                                                  +-- Risk Scorer (5-signal, 0-100)
                                                                  +-- Triage Evaluator (4-rule cascade)
                                                                  +-- LLM Provider (OpenAI / Mock)
                                                                  +-- Response Validator
                                                                  +-- Session Repository (in-memory)
```

**Request pipeline**: User message -> PII anonymization -> risk scoring -> triage check -> LLM response (or safety override) -> response validation -> real-time SSE delivery.

**API endpoints** (REST, JSON -- compatible with existing healthcare systems):

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/chat/` | Synchronous chat |
| `POST /api/v1/chat/stream` | Real-time SSE streaming |
| `GET /api/v1/chat/{id}/history` | Conversation history |
| `POST /api/v1/chat/{id}/handoff` | Manual professional handoff (returns context for EHR/EMR integration) |

## Risk Detection

Composite score (0-100) from 5 signals:

| Signal | Max | Description |
|--------|-----|-------------|
| Keywords | 30 | 3 severity tiers, bilingual (EN/ES) |
| Sentiment | 20 | Negative word counting |
| Behavioral | 20 | Message length, ALL CAPS, excessive punctuation |
| Escalation | 15 | Distress phrases ("i can't anymore", "nothing matters") |
| Session history | 15 | Cumulative risk trend over time |

Classification: **Low** (0-29) | **Medium** (30-59) | **High** (60-79) | **Critical** (80-100)

## Triage and Human Handoff

4 cascading rules (first match wins):

| # | Rule | Trigger | Action |
|---|------|---------|--------|
| 1 | User requests human | "talk to a real person", "hablar con alguien" | Immediate handoff |
| 2 | Critical risk | Score >= 80 | Handoff + crisis resources (Mexican hotlines) |
| 3 | High risk | Score >= 60 | Professional handoff |
| 4 | Long session | 15+ messages | Check-in, offers professional support |

**Chatbot limits**: Never diagnoses, never recommends medication, never decides escalation (rules-only). A Response Validator blocks unsafe LLM outputs and replaces them with safe fallbacks.

**Mexico crisis resources** (delivered on critical risk): Linea de la Vida (800-911-2000), SAPTEL (55 5259-8121), 911.

## Privacy and Security

1. **PII Anonymization** -- Emails, phones, names, and addresses are stripped before reaching the LLM. Replaced with `[EMAIL]`, `[PHONE]`, `[NAME]`, `[ADDRESS]`.
2. **No persistent storage** -- In-memory sessions only. Nothing written to disk or database. All data lost on restart.
3. **Response filtering** -- LLM output is validated against blocked patterns (diagnoses, medication, minimizing language) before delivery.
4. **Additional**: CORS restriction, no PII in logs, Pydantic input validation, provider-agnostic LLM config.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI, Pydantic v2 |
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Zustand |
| LLM | OpenAI API (provider-agnostic) |
| Streaming | Server-Sent Events (SSE) |
| Infrastructure | Docker, Docker Compose |
| Testing | pytest, pytest-asyncio |

## Quick Start

```bash
# 1. Configure
cp backend/.env.example backend/.env
# Edit backend/.env: set LLM_PROVIDER, LLM_API_KEY, LLM_MODEL

# 2. Run
docker compose up --build

# 3. Open
# Frontend:  http://localhost:3000
# API docs:  http://localhost:8001/docs

# 4. Test
cd backend && pytest tests/ -v
```

## Example Flow

```
User:  "I've been feeling stressed"        -> Score: 12 (low)      -> Normal LLM response
User:  "I feel hopeless"                   -> Score: 62 (high)     -> Triage: handoff to professional
User:  "I want to kill myself"             -> Score: 85 (critical) -> Triage: handoff + crisis hotlines
User:  "I want to talk to a real person"   ->                      -> Triage: immediate handoff
```
