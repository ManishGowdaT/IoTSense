# Phase 7 — Authentication, roles and audit trail

**Status:** Authentication and initial user administration implemented; local runtime and role scenarios have not been exercised in this workspace.

## Delivered

- Passwords are hashed with Argon2 through `pwdlib`; login uses a generic failure response and a dummy hash for unknown/inactive accounts.
- Opaque random session credentials are stored only as SHA-256 hashes. Sessions expire, rotate on refresh, revoke on logout/password reset/deactivation, and are held in HttpOnly, SameSite=Strict cookies.
- A separate CSRF cookie is checked against both the submitted `X-CSRF-Token` header and the session’s stored token hash for state-changing browser requests.
- Login attempts are throttled per client IP and normalized email. Password reset requests are throttled and return a generic 202 response. Single-use, expiring reset/invitation tokens are stored only as hashes.
- `/api/v1/auth/login`, `logout`, `refresh`, `me`, `password-reset/request` and `password-reset/confirm` are implemented.
- `/api/v1/users` supports organization-scoped listing and invitations. Facility Admins can invite/deactivate Maintenance Staff and Viewers in their own organization. Super Admins can manage platform-wide users. Deactivation revokes active sessions.
- Password resets, login/logout, user invitations/deactivation and initial administrator creation write audit records. Error responses use a redacted `application/problem+json` envelope.
- Alembic revision `0002_auth_sessions` adds session and reset-token storage. `0001_initial_schema` remains the base domain schema.
- Added interactive local bootstrap tools for the first Super Admin and initial organization.

## Local initialization

Follow [backend setup](../../backend/README.md). Create the first Super Admin and an organization with the operator scripts. To invite tenant users, configure SMTP values in the untracked `backend/.env`; reset and invitation tokens are never returned by API responses or logged. Cookies should use `SECURE_COOKIES=true` whenever the API is accessed over HTTPS.

## Role and tenant rules

| Role | Current user-management access |
|---|---|
| `super_admin` | Lists users across organizations; invites users into an organization or platform scope; deactivates users except itself |
| `facility_admin` | Lists only its own organization; invites/deactivates only Maintenance Staff or Viewers in that organization |
| `maintenance_staff` | No user-administration access |
| `viewer` | No user-administration access |

The shared `require_roles` dependency is available for subsequent protected routes. Frontend role hiding remains a usability feature; this API enforces authorization on the server.

## Limitations carried forward

- Login throttling is in-process memory. It is suitable only for this single-process development foundation; production deployment must use a shared rate-limit store and must retain network-level throttling.
- SMTP is the only reset/invitation delivery path and must be configured; otherwise password-reset requests remain generic but do not send mail, and invitation creation returns 503.
- Organization/facility provisioning beyond the local organization bootstrap, facility-level membership, user profile/password change, and full authorization for operational resources remain later work.
- The system was not started and no tests were run for this phase. The phase exit gate—demonstrating four role accounts and cross-organization denials—remains open until an environment with PostgreSQL and SMTP is configured and scenarios are exercised.
