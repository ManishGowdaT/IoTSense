# IoTSense

Smart washroom hygiene monitoring and facility operations platform.

IoTSense is being created from scratch. The planned system connects ESP32 devices to a Python API and PostgreSQL database, then presents operational status and workflows in a React web app.

## Demo MVP

The **frontend MVP** includes sample dashboard, washroom, alert, cleaning, device and analytics flows. It can also read MQ-3 and MQ-135 sensor outputs directly from an ESP32 USB serial connection; temperature, humidity and pressure are labeled simulated BME680 values. It needs Node.js and npm; **PostgreSQL, Docker and the Python backend are not needed**.

Without an ESP32 connection, dashboard values use sample data. With hardware attached, the live sensor values are displayed in the dashboard but are not stored in the backend.

```powershell
npm --prefix .\frontend install
npm --prefix .\frontend run demo
```

Open the localhost URL printed by Vite and select **Connect ESP32** in the top banner. The browser must be Chrome or Edge and the device sketch must be uploaded first. If port 4173 is busy, Vite will select another port. See [frontend MVP instructions](frontend/README.md) for wiring and upload steps.

## Development status

The separate FastAPI/PostgreSQL backend includes authentication foundations, device provisioning and telemetry ingestion. This MVP uses direct USB serial for the browser walkthrough; API persistence and production device transport are separate follow-on integration work.

## Planned components

- `frontend/` — React, Vite, TypeScript web application
- `backend/` — FastAPI service, domain logic and database migrations
- `firmware/esp32/` — ESP32 serial sketch for live MQ sensor demo
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

## Data integrity rule

Live hardware readings and generated simulation data must always be distinguishable. MQ sensor outputs are relative indices unless calibrated; the application must not present unsupported ppm, pathogen-detection or cleaning-certification claims.
