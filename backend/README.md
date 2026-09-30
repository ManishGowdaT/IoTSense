# Backend development setup

Phases 6–8 create the FastAPI process, PostgreSQL connection, SQLAlchemy domain models,
Alembic migrations, health/readiness endpoints, cookie sessions, CSRF protection,
initial role-scoped user administration, device provisioning and telemetry ingestion.
Most operational APIs remain for later phases.

## Requirements

- Python 3.11 or newer
- Docker Desktop with Docker Compose

## Windows PowerShell setup

Run these commands from the repository root:

```powershell
cd backend
Copy-Item .env.example .env
docker compose up -d postgres
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
alembic upgrade head
python -m scripts.create_super_admin
python -m scripts.create_organization
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If PowerShell blocks virtual-environment activation, use `\.venv\Scripts\python.exe`
instead of `python` for the install and startup commands.

Then open `http://127.0.0.1:8000/api/v1/health`,
`http://127.0.0.1:8000/api/v1/ready` or `http://127.0.0.1:8000/api/v1/docs`.
The readiness route returns HTTP 503 when PostgreSQL cannot be reached.

For browser access, `CORS_ORIGINS` in `.env.example` allows the local Vite origin.
Keep `SECURE_COOKIES=false` only for local HTTP development. Set it to `true` behind
HTTPS. Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM_EMAIL` and, if required,
`SMTP_USERNAME`/`SMTP_PASSWORD` before inviting tenant users or delivering password
reset instructions. User invitations require email delivery; tokens are never exposed
in API responses or logs.

After the API is running, authenticate at `POST /api/v1/auth/login`. Browser mutations
such as logout, refresh, invitations and user deactivation require the CSRF token from
the `iotsense_csrf` cookie in the `X-CSRF-Token` header. `GET /api/v1/auth/me` returns
the current user and organization scope. `POST /api/v1/users` creates an invitation;
`DELETE /api/v1/users/{id}` deactivates that user and revokes their sessions.

Administrators can provision devices at `POST /api/v1/devices`; the returned
`device_key` is shown once. Store it in the device's protected configuration. The API
stores only its SHA-256 digest. Rotate with `POST /api/v1/devices/{id}/rotate-key` or
revoke with `POST /api/v1/devices/{id}/revoke`; these browser mutations require the
CSRF header. Authenticated devices submit readings to `POST /api/v1/telemetry` with
`X-Device-Key`. The deprecated `POST /api/ingest` path uses the same validator and
storage path. Telemetry is tagged `live_hardware` by the server; device payloads cannot
select a source mode. MQ measurements are stored as raw or relative values, not ppm.

The compose credentials are for local development only. Replace them with managed
secrets and a restricted database user before deploying anywhere shared or public.
Login throttling currently uses process memory, so run only one API process locally;
production must use a shared rate-limit store and edge/network throttling.

## Schema changes

Create a migration from the backend directory with:

```powershell
alembic revision --autogenerate -m "describe schema change"
```

Review generated SQL before committing it. Apply with `alembic upgrade head`; inspect
the current revision with `alembic current`. Migrations must remain explicit and
reversible where practical.
