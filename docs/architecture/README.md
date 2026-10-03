# Architecture

SIMA uses a modular monolith.

High-level layering:

```text
React UI
  ↓
FastAPI HTTP layer
  ↓
Application Services / Policies
  ↓
Repositories
  ↓
PostgreSQL
```

See CP-03 for the architecture baseline.
