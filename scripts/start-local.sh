#!/usr/bin/env bash
set -e

docker compose up -d postgres

(cd backend && source .venv/bin/activate && python seed.py && uvicorn app.main:app --reload --port 8000) &
(cd frontend && npm run dev) &
wait
