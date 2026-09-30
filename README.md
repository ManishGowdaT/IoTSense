# IoTSense

Smart washroom hygiene monitoring and facility operations platform.

IoTSense is being created from scratch. The planned system connects ESP32 devices to a Python API and PostgreSQL database, then presents operational status and workflows in a React web app.

## Project status

**Current phase:** Phase 7 — authentication, roles and audit.

The frontend prototype, routing/configuration foundation, domain/API contract, FastAPI process scaffold, PostgreSQL models and migrations, and initial authentication/role/audit foundation are in place. Telemetry ingestion and hardware integration have not started.

## Planned components

- `frontend/` — React, Vite, TypeScript web application
- `backend/` — FastAPI service, domain logic and database migrations
- `firmware/esp32/` — device firmware and telemetry client
- `docs/` — product, architecture, hardware and operations documentation
- `infra/` — local/deployment configuration
- `tests/` — cross-component and end-to-end test material
- `tools/` — development utilities

See [Phase 0 baseline](docs/phase-0/phase-0-baseline.md) for decisions, confirmed facts and open questions.
See the [Phase 1 UX blueprint](docs/product/phase-1-ux-blueprint.md), [Phase 2 design system](docs/product/phase-2-design-system.md), and [Phase 3 prototype notes](docs/product/phase-3-prototype.md).
See [Phase 4 frontend foundation](docs/product/phase-4-frontend-foundation.md) for route, role-policy and API-boundary details.
See [Phase 5 domain and API contract](docs/architecture/phase-5-domain-and-api-contract.md) and [OpenAPI](backend/openapi.yaml).
See [Phase 6 backend foundation](docs/product/phase-6-backend-foundation.md) and [backend setup](backend/README.md).
See [Phase 7 authentication and access control](docs/product/phase-7-auth-and-authorization.md).

## Run the frontend prototype

```powershell
cd frontend
npm install
npm run dev
```

## Run the backend foundation

Follow the [backend setup instructions](backend/README.md) to start local PostgreSQL, apply the initial migration and run FastAPI.

## Data integrity rule

Live hardware readings and generated simulation data must always be distinguishable. MQ sensor outputs are relative indices unless calibrated; the application must not present unsupported ppm, pathogen-detection or cleaning-certification claims.
