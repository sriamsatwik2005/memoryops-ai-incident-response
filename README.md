# MemoryOps — AI Incident Response Agent

MemoryOps is an AI incident-response platform that investigates production incidents using current operational evidence and persistent organizational memory through Hindsight.

## Core idea

1. An incident is created from logs/metrics/deployment context.
2. FastAPI sends the incident to the agent.
3. The agent searches Hindsight for relevant historical incidents.
4. The LLM combines current evidence with recalled experiences.
5. The agent recommends a remediation with supporting reasoning.
6. A human approves the remediation.
7. The resolved incident is retained in Hindsight as a new experience.
8. Future incidents can recall that experience.

This creates the core learning loop:

`Incident → Investigate → Recall → Recommend → Resolve → Retain → Better future response`

## Architecture

```text
React/Vite → FastAPI → Incident Agent → LLM
                              └──────→ Hindsight
                              └──────→ PostgreSQL
```

## Stack

- Frontend: React + Vite + TypeScript
- Backend: FastAPI + Python
- Database: PostgreSQL
- Agent: Python tool/orchestration layer
- Memory: Hindsight
- LLM: OpenAI-compatible endpoint (default configuration targets Groq)
- Deployment target: Docker + cloud platform

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker
- Hindsight Cloud account/API key OR a local Hindsight server
- LLM API key

Hindsight's official Python client supports `retain`, `recall`, and `reflect`; this starter uses `retain` and `recall` directly so the memory loop is visible and controllable. See the official Hindsight documentation before changing SDK behavior.

## 1. Start PostgreSQL

```bash
docker compose up -d postgres
```

## 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in:

```env
HINDSIGHT_API_KEY=your_hindsight_key
LLM_API_KEY=your_llm_key
```

The Hindsight bank ID is:

```env
HINDSIGHT_BANK_ID=memoryops-incidents
```

Then run:

```bash
python seed.py
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173

## First demo

Use `INC-1108` for an incident that has not yet been investigated.

For the strongest Hindsight demo, first seed/retain one or two resolved incidents in your Hindsight bank, then investigate a new incident with similar symptoms. The UI will display the recalled memories alongside the agent's analysis.

## Hindsight memory design

### Retain after resolution

Store an incident as an experience containing:

- incident ID
- service
- symptoms
- logs
- metrics
- deployment
- root cause
- remediation
- outcome

### Recall during investigation

Query Hindsight with the current incident's service, symptoms, logs, metrics, and deployment context. Limit the returned memories to the most relevant experiences/observations before passing them to the LLM.

## Production hardening later

This repository is the starting point, not the final production implementation. Before the final demo, add:

- authentication/RBAC
- background job queue for long-running investigations
- structured log ingestion
- metrics integration
- runbook retrieval
- audit trail
- rate limiting
- secrets management
- automated tests
- Dockerfiles and CI/CD
- deployment to a cloud platform
- observability for the agent itself

## Security rule

Never commit API keys. Do not give the agent unrestricted shell access or unrestricted production credentials. Keep remediation human-approved for the hackathon prototype.
