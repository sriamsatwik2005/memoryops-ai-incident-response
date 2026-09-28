# MemoryOps Architecture

## Runtime flow

```text
Engineer
  ↓
React UI
  ↓ HTTP/JSON
FastAPI API
  ↓
Incident Agent
  ├── PostgreSQL: current incident + structured data
  ├── Hindsight: historical experiences
  └── LLM: reasoning
  ↓
Investigation result
  ↓
React UI
  ↓
Human approval
  ↓
Resolution
  ↓
Hindsight retain
```

## Memory boundary

PostgreSQL is the system-of-record for structured application state. Hindsight is the agent's long-term memory layer. Do not duplicate every database row into memory; retain information that is useful for future reasoning, especially causes, actions, outcomes, and operational lessons.
