# Phase 8 — Device registry and telemetry ingestion

**Status:** Implementation added; database-backed acceptance scenarios have not been run.

## Delivered

- Administrator-only device provisioning to an existing washroom, scoped to the user's organization for Facility Admins.
- One-time random device credentials. Only a SHA-256 digest is stored; credentials can be rotated or revoked. Provisioning and credential changes are audited.
- Paginated device listing and device detail with tenant-scoped access for all four roles.
- `POST /api/v1/telemetry` and compatibility `POST /api/ingest`, both using the same device-key authentication, validation, idempotency and persistence service.
- Request identity is bound to the device credential. The server assigns `live_hardware`; the client cannot set source mode, organization, washroom or derived score.
- Telemetry stores raw values and quality separately, associates known sensor keys, records firmware and freshness, and treats missing values as null rather than zero.
- Sequence retries with identical normalized payloads return the existing event; reused sequences with different content return `409`.
- Input checks cover timezone-aware timestamps, configurable future/past replay windows, payload Content-Length, observation count, finite numeric values, known units and metric ranges. MQ ppm is not accepted.

## Local configuration

`TELEMETRY_MAX_CLOCK_SKEW_SECONDS` defaults to 900, `TELEMETRY_MAX_PAST_AGE_SECONDS` to 86400, and `TELEMETRY_MAX_PAYLOAD_BYTES` to 65536. These values should be adjusted to the device's clock and offline queue behavior before deployment.

## Acceptance still open

- Start PostgreSQL, apply the existing schema migrations, provision a device and exercise accepted, duplicate, conflicting, malformed, out-of-range and revoked-key requests.
- Verify cross-organization device listing, detail, provisioning and revocation denials with the four roles.
- Confirm the firmware payload and its actual sensor keys/units against the schema. Hardware identity and calibration remain unverified.
- The API accepts only the documented units: `Cel`, `%`, `Pa`, `Ohm`, `count`, `V`, and `1` for their corresponding metrics.

## Checks performed

- Python syntax compilation passed for the backend application modules.
- Database/API scenarios and live hardware checks could not be run in this workspace: Docker is unavailable, there is no local backend virtual environment or `.env`, the system Python lacks the project dependencies and pytest, and `backend/tests` has no test cases yet.
