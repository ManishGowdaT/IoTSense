# Phase 6 — Backend foundation

**Status:** Implementation scaffold complete; local runtime not started in this workspace.

## Delivered

- FastAPI application with versioned API docs URL, request IDs, structured request logs and a redacted problem response for unexpected errors.
- `/api/v1/health` process liveness endpoint and `/api/v1/ready` PostgreSQL dependency check.
- Environment-backed configuration, SQLAlchemy engine/session dependency and named metadata conventions.
- SQLAlchemy models for the Phase 5 organization, facility, user, washroom, device, sensor, telemetry, score, incident, cleaning, audit and notification entities.
- Explicit initial PostgreSQL migration (`0001_initial_schema`) with UUID identifiers, timestamp defaults, foreign keys, unique constraints and query indexes.
- Docker Compose PostgreSQL 16 service for local development and Windows setup instructions.

## Start locally

Follow [backend development setup](../../backend/README.md). This phase does not seed demo users or telemetry. The readiness route is expected to fail with 503 until PostgreSQL is running and the migration has been applied.

## Scope boundary

This is the process and persistence foundation only. Login/session security, authorization, tenant-scoped business routes, device credential provisioning, telemetry ingest and validation, scoring, alerts, cleaning workflows and notification delivery are not implemented here. The Phase 5 OpenAPI document remains the target contract for those subsequent phases.

No tests were run as part of this phase.
