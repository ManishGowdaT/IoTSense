# Phase 4 — Frontend application foundation

**Status:** Foundation implemented around the Phase 3 prototype.

## Delivered

- Added React Router with stable paths for all 20 screens; browser back/forward and direct links map to the selected screen.
- Added unknown-route fallback to the Dashboard.
- Added role-aware route policy and navigation filtering for Super Admin, Facility Admin, Maintenance Staff and Viewer. The active prototype identity is Facility Admin.
- Added typed domain contracts for sensor observations, data quality/source, washroom status, telemetry envelopes and hygiene scores.
- Added a central API request boundary with same-site credential behavior and normalized API errors. It does not persist access tokens in browser local storage.
- Added environment configuration for API base URL, data mode and app name, plus a frontend `.env.example`.
- Added a typed dashboard API service as the future integration point; current screens continue to use clearly labeled fixtures.
- Preserved the Phase 3 UI and interactions.

## Important boundary

Frontend route/role checks are navigation hints only. The backend must enforce authentication, organization scope and authorization for every protected endpoint and action. Authentication and API integration are not implemented in this phase.

## Local setup

From `IoTSense/frontend`:

```powershell
npm install
npm run dev
```

Environment defaults are in `.env.example`. Current prototype data mode remains `sample`; changing an environment value does not create a live hardware connection.

## Known limitation

The Vite dev server could not be previewed from the managed workspace because its dependency optimizer attempted a parent-directory scan denied by the sandbox. Dependencies installed successfully. This is an execution-environment filesystem restriction; it does not establish that the app works at runtime, so local browser review remains an outstanding acceptance item.

## Phase 4 completion checklist

- [x] Route map and direct-link path model added.
- [x] Shared API client boundary and configuration added.
- [x] Typed domain contracts added.
- [x] Role-aware frontend navigation/route policy added.
- [x] Preserve fixture mode and common visible error/empty/offline states.
- [ ] Run the app in a normal local development environment and review all routes visually.
- [ ] Adjust the prototype after that review before beginning API contract implementation.
