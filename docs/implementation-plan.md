# IoTSense — Phase-wise Software Implementation Plan

**Purpose:** Build IoTSense as a maintainable IoT product for washroom hygiene monitoring and facility operations, while accurately representing what the sensors can and cannot establish.

**Planning basis:** This plan follows the supplied project prompt and reconciles it with the project context in this chat: an ESP32, a BME680 that has recently reported offline, and MQ sensor readings. The prompt’s final screen inventory contains **20 screens**; that supersedes its earlier reference to 17. Preserve and extend the existing React/Vite dashboard and Python simulator/backend rather than replacing them without first inspecting them.

## Product and evidence rules

- End-to-end flow: **ESP32 → authenticated HTTPS ingestion API → Python backend → stored telemetry → versioned hygiene/cause rules → React dashboard and operations workflows**.
- The product has two explicit data modes: **Live Hardware** and **Simulation**. Every value and chart discloses its mode and last update. Simulation data must never appear as a live sensor observation.
- Until calibrated against an appropriate reference method, MQ-135/MQ-3 outputs are **relative sensor indices**, not certified gas concentrations or ppm. Do not claim pathogen detection, clinical/industrial certification, medical diagnosis, or definitive proof that cleaning succeeded. Say “indicators” and “sensor-based evidence.”
- Hardware currently evidenced in chat is not yet a reliable complete sensor set: the BME680 has recently printed `Offline`/failed initialization; MQ-135 has appeared in analog readings; MQ-3 is not confirmed connected. Reconcile actual board wiring, sensor availability and claims before enabling those features.
- Measure the BME680 board’s address. Bosch SDO low normally selects `0x76`, and SDO high selects `0x77`; prior notes saying SDO-to-GND with `0x77` conflict. Use an I²C scan and chip-ID check (`0x61`) to establish actual configuration.

## Architecture and proposed stack

- **Web:** React, Vite, TypeScript, Tailwind CSS, React Router, and Recharts or Chart.js.
- **API/backend:** Python, FastAPI, Pydantic, SQLAlchemy, Alembic and pytest.
- **Storage:** PostgreSQL. Keep raw telemetry and derived records distinguishable and traceable to a scoring-engine version.
- **Device:** ESP32 publishes validated, timestamped telemetry over HTTPS. Use per-device identity/credentials; do not embed shared production secrets in firmware or source control.
- **Hosting/operations:** Render for frontend, API and managed PostgreSQL; GitHub for version control and CI/CD; health/readiness endpoints, structured logs, metrics and error reporting.

## Screen inventory (20)

1. Landing page; 2. Login; 3. Forgot password; 4. Dashboard; 5. Washrooms list; 6. Washroom detail/live monitor; 7. Sensor detail; 8. Hygiene analysis; 9. Cause identification; 10. Analytics; 11. Alerts/incidents; 12. Cleaning operations; 13. Cleaning-event verification; 14. Devices list/detail; 15. Device provisioning/setup; 16. Users and roles; 17. Settings; 18. Audit logs; 19. System health; 20. Profile.

Primary navigation should foreground Dashboard, Live Washroom Monitoring, Hygiene Analysis, Alerts, Cleaning Operations and Analytics. Cause identification, sensors, devices and cleaning history are supporting workflows. Users, settings, audit and system health are administrative. Use a responsive sidebar/drawer or mobile navigation. Use status colors consistently: green clean, amber moderate, red dirty, grey offline, blue/purple cleaning; always pair color with text/icon for accessibility.

## Roadmap overview

The plan has 18 delivery phases plus Phase 0. Phases 1–3 produce the UX and frontend prototype first, as requested in the supplied prompt. Repository discovery, requirements reconciliation and hardware diagnosis are foundation work, not a reason to delay the UI prototype. API/data contracts can be agreed during design; backend implementation begins after the screen prototype is reviewable.

| Phase | Focus | Main exit gate |
|---|---|---|
| 0 | Existing-project audit and scope baseline | Existing code, claims, hardware and gaps documented |
| 1 | Product flows and UX architecture | 20 screens, roles and critical journeys mapped |
| 2 | Design system and interaction specification | Reusable components and states agreed |
| 3 | Screen prototype with marked sample data | All 20 screens navigable and reviewable |
| 4 | Frontend application foundation | Routes, layout, types, error/loading/empty states in place |
| 5 | Data model and API contracts | Versioned schemas and migration plan agreed |
| 6 | Backend foundation and database | API, PostgreSQL, migrations and health checks run locally |
| 7 | Authentication, roles and audit | Protected routes and object-level authorization demonstrated |
| 8 | Device registry and telemetry ingestion | Authenticated telemetry persists safely and idempotently |
| 9 | Hygiene score, cause rules and alert engine | Versioned, explainable rules work against known fixtures |
| 10 | Simulation and live-mode state | Simulation is safe, obvious, repeatable and independent of live data |
| 11 | Frontend/API integration | Dashboard and workflows consume real API contracts |
| 12 | ESP32 and sensor integration | Hardware telemetry passes bench gate and arrives end to end |
| 13 | Cleaning operations and verification workflow | Task/event lifecycle and sensor evidence are traceable |
| 14 | Analytics and operational views | Trends and filters reconcile to stored data |
| 15 | Security, reliability and quality assurance | Release checklist and failure scenarios pass |
| 16 | Deployment and observability | HTTPS production-like deployment is monitored and recoverable |
| 17 | Documentation, demo and release | User, operator and developer guides match shipped behavior |

## Phase 0 — Audit and scope baseline

**Goal:** Learn what already exists and establish a truthful definition of the first release.

**Work:**
- Inspect the existing repository, branches, frontend, simulator/backend, database, Arduino sketches, environment files, build/deployment configuration and README before editing. Record what works; keep useful code.
- Inventory the actual board and sensor setup: ESP32 pin labels, sensor pin labels, power, common ground, I²C scan result, chip ID, ADC pins and divider values. Do not infer wire identity from color alone.
- Reconcile the paper’s planned sensors/functions with hardware actually present. Record BME680 as currently unverified/offline and MQ-3 as unconfirmed until demonstrated.
- Create a requirements ledger: release-one requirement, later enhancement, hardware-dependent or out of scope. Record decisions, owners and dependencies.
- Define safe product vocabulary: relative indices, sensor indicators, estimated/heuristic score, simulation and sensor-based cleaning evidence.

**Deliverables:** repository map; current-state diagram; sensor/pin inventory; assumptions and risks log; prioritized release-one scope; definition of done.

**Exit gate:** No feature is called live without an identified live-data source. Unknown hardware facts remain explicit dependencies, not guessed pins or sensors.

## Phase 1 — Product flows and UX architecture

**Goal:** Turn the feature list into coherent user journeys before implementing the application.

**Work:**
- Define four roles: Super Admin, Facility Admin, Maintenance Staff and Viewer. Map actions and data visibility to each.
- Map critical journeys: sign in/reset password; see site status; inspect a washroom and sensor freshness; investigate a cause; acknowledge/resolve an incident; assign/start/complete cleaning; inspect before/after evidence; provision/diagnose a device; review trends; administer users/settings.
- Define information hierarchy/navigation for all 20 screens. Specify links, filters, search, pagination, breadcrumbs and mobile navigation.
- Define operational states: clean/moderate/dirty, cleaning, device offline, sensor missing/invalid, stale telemetry, maintenance and simulation. “Unknown” or “stale” must not silently appear clean.
- Specify screen-level data needs, empty/error/loading states, units, timestamps and accessibility.

**Deliverables:** sitemap; role/action matrix; journey maps; screen inventory and low-fidelity wireframes; terminology/state glossary.

**Exit gate:** A user can trace alert-to-cleaning-to-review, and each screen has a documented purpose and data source.

## Phase 2 — Design system and interaction specification

**Goal:** Set visual and interaction standards consistently across prototype and product.

**Work:** Define typography, spacing, grid, card/table/chart treatments, responsive breakpoints and focus states. Define status tokens and text/icon labels; maintain contrast and never rely on color alone. Specify reusable components: app shell, site/washroom selector, score/sensor cards, freshness badge, mode banner, timeline, alert row, task status, confirmation dialog and empty/error states. Use a premium, minimal, clinical/industrial IoT visual language with readable density, whitespace, restrained gradients and clear hierarchy. Define chart conventions for units, period, missing data, simulation data and thresholds.

**Deliverables:** design tokens; component inventory; responsive behavior notes; interaction/accessibility specification.

**Exit gate:** Core states are visually distinguishable and repeatable across all screens.

## Phase 3 — Complete UI prototype using fixtures

**Goal:** Build and review the full user-facing experience before backend implementation.

**Work:**
- Implement all 20 screens as navigable prototype pages in the existing frontend where feasible.
- Use named fixture data with a visible **SIMULATION / SAMPLE DATA** banner. Never make mock values look like connected readings.
- Include scenarios for normal, moderate, dirty, cleaning, recovery, sensor failure and device offline; fixtures also cover missing and stale values.
- Build dashboard summaries, washroom list/detail, sensor views, analysis/cause views, analytics, incident and cleaning workflows, devices/provisioning, administration, audit, health and profile.
- Include responsive layout and keyboard navigation. Use “Intelligence Engine” only if explicitly described as rule-based; do not advertise AI without implemented ML.
- Review with the project owner and revise navigation, terminology and priorities before wiring real APIs.

**Deliverables:** clickable prototype; fixture catalog; screen/state checklist; recorded design decisions.

**Exit gate:** All 20 screens and key journeys can be demonstrated with clearly marked sample data and no dead-end navigation.

## Phase 4 — Frontend application foundation

**Goal:** Make the reviewed prototype a maintainable React application.

**Work:** Preserve existing Vite/React code and refactor incrementally. Establish TypeScript strictness suited to the current codebase, route layout, shared components, feature folders, API client boundary and environment configuration. Define typed frontend models from agreed contracts. Add route guards and role-aware navigation (the backend remains the authorization authority). Implement common loading, empty, offline, stale-data, validation and API-error patterns. Avoid duplicating server-side business logic. Add accessible forms, confirmation for consequential actions and responsive behavior.

**Deliverables:** application shell, route map, shared component library, typed client boundary, frontend configuration and run instructions.

**Exit gate:** Prototype screens run through the normal app structure and can consume API data.

## Phase 5 — Domain model and API contracts

**Goal:** Agree on stable data and endpoint contracts before implementations diverge.

**Core entities:** organizations; users and roles; washrooms; devices; sensors; raw sensor readings; derived hygiene scores; alerts/incidents; cleaning tasks/events; device events; audit logs; notification preferences. Establish ownership (organization → users/washrooms → devices → sensors → readings) and retention expectations.

**Work:** Define identifiers, timestamps/time zones, units, missing semantics, status, source mode, calibration metadata and provenance. Telemetry includes device ID, device timestamp, readings, firmware version and sequence/idempotency ID. Represent BME680 temperature, humidity, pressure and gas resistance only when actually available. Represent MQ readings as raw ADC/voltage plus relative-index metadata, not unsupported ppm. Define response, pagination, filtering and error formats; use OpenAPI as shared reference. Preserve `/api/ingest` compatibility if deployed or in use; introduce `/api/v1/telemetry` and route both through one validated ingestion service during transition.

**Initial endpoints:**
- `/api/v1/auth/login`, logout, refresh, password reset and current user
- `/api/v1/telemetry` (plus compatibility alias `/api/ingest` if needed)
- `/api/v1/dashboard`, `/api/v1/washrooms`, washroom detail/history
- `/api/v1/sensors/{id}`, `/api/v1/alerts` and acknowledge/resolve actions
- `/api/v1/cleaning/tasks` and task start/complete/event actions
- `/api/v1/analytics`, `/api/v1/devices` and provisioning actions
- `/api/v1/users`, `/api/v1/settings`, `/api/v1/audit-logs`
- `/health` and `/ready`

**Deliverables:** entity relationship diagram; OpenAPI spec; telemetry fixtures; compatibility/deprecation policy; retention and migration notes.

**Exit gate:** UI, API and firmware agree on fields, units, freshness, authentication and source-mode tagging.

## Phase 6 — Backend foundation and database

**Goal:** Establish a reliable local service and schema.

**Work:** Create/extend FastAPI with config, structured logging, request IDs, consistent errors and modules for auth, telemetry, washrooms, devices, alerts, cleaning, analytics and administration. Implement SQLAlchemy models and Alembic migrations; index time-series lookups and organization/washroom/device filters. Keep raw input immutable/auditable and derived values traceable to algorithm version. Set up PostgreSQL locally and environment-based configuration. Use transactions appropriately; plan retention/aggregation before high-volume growth. Add liveness/readiness checks distinguishing process health from database readiness.

**Deliverables:** local backend/database; migrations; API docs; structured logs; local setup guide.

**Exit gate:** A clean database migrates from scratch and service health accurately reflects dependencies.

## Phase 7 — Authentication, roles and audit trail

**Goal:** Protect user and facility data before exposing operations.

**Work:** Implement secure password hashing, login throttling, short-lived sessions/tokens, refresh/revocation, logout and password reset. Keep secrets out of frontend and repository. Enforce role-based and organization/object-level authorization on every protected endpoint; hiding a frontend button is not access control. Add user provisioning/deactivation and least-privilege rules for device setup, thresholds, incident closure and task completion. Audit security-sensitive and operational changes with actor, action, target, timestamp and result; never log credentials.

**Deliverables:** auth endpoints; role/action policy; protected routes; audit events; security configuration.

**Exit gate:** Four role accounts can only perform authorized actions, including denial of cross-organization access.

## Phase 8 — Device registry and telemetry ingestion

**Goal:** Receive device data safely and preserve trustworthy provenance.

**Work:** Register devices to organization/washroom, issue revocable per-device credentials, track firmware and last-seen time, and support rotation/revocation. Validate schema, timestamp bounds, device authorization, sensor ranges and payload size. Normalize units and retain original raw values. Handle duplicate/retried requests idempotently; reject or quarantine malformed, unauthorized or implausibly old/future events observably. Store telemetry and update freshness/status. Represent missing/invalid sensors explicitly; they must not crash ingestion or produce invented values. Rate-limit and protect deployed device routes with HTTPS.

**Deliverables:** device lifecycle and ingestion endpoints; raw storage; validation/error metrics; device client contract.

**Exit gate:** Authorized telemetry can be queried with correct source, units and timestamps; duplicates do not create duplicate logical events.

## Phase 9 — Versioned hygiene, cause and alert engines

**Goal:** Produce explainable, testable operational indicators.

**Work:** Specify/version an initial engine such as `hygiene-v1`. Separate validation, baseline correction, normalization, feature calculation, weighting, score, classification, cause indicators and alert evaluation. Centralize thresholds and audit changes. Start with transparent heuristics; do not treat paper formulas as scientific truth without review/calibration. Treat MQ-135 as a relative response, not exact NH3/VOC concentration. Use BME values only when valid and fresh. Do not use MQ-3 alcohol or a cleaning bonus until MQ-3 is connected and interpretation validated. Avoid assuming humidity is always harmful or monotonic temperature/humidity contributions are meaningful. Define valid ranges, warm-up, baseline drift, outliers, stale windows and quality flags. Causes are ranked evidence with time window/data quality/cautious confidence wording, not certainty. Alerts have severity, deduplication/cooldown, acknowledge/resolve state and evidence links; creation is idempotent.

**Deliverables:** score/cause/alert specification; versioned engine; explainability fields; known-input/expected-output fixtures; calibration plan.

**Exit gate:** Every displayed score/cause traces to inputs, quality flags, thresholds and engine version. Missing/stale data yields unknown/degraded state, never fabricated certainty.

## Phase 10 — Simulation and live-mode state

**Goal:** Support demos and development without confusing synthetic and live data.

**Work:** Implement repeatable Normal, Moderate, Dirty, Cleaning, Recovery, Sensor Failure and Device Offline scenarios. Tag simulation records with source mode, scenario ID and generated timestamps; isolate them from live device data. Define one authoritative mode rule. The prompt suggests simulation after roughly 20 seconds without telemetry; make interval configurable and display **last live update** and switch reason. Never silently substitute synthetic readings in a live chart. Provide an authorized demo control, log mode changes and prevent production telemetry overwrite.

**Deliverables:** simulator, scenario fixtures, mode state contract and UI banner/controls.

**Exit gate:** Device disconnection results in stale/offline status; simulation is visibly labelled and cannot be mistaken for current hardware.

## Phase 11 — Frontend/API integration

**Goal:** Replace prototype fixtures with authenticated services progressively.

**Work:** Connect login, dashboard, washrooms, details, freshness, analytics, alerts, cleaning and device views. Implement loading, empty, stale/offline, permission-denied and recoverable-error states. Keep fixtures only behind explicit simulation/demo configuration. Display dashboard score thresholds (80–100 clean, 50–79 moderate, 0–49 dirty) only after approved/versioned; explain score and show last update/mode together. Support 30-minute through 7-day and custom time windows with consistent timezone, aggregation and visible missing data. Separate observed readings, derived indicators and threshold lines in charts.

**Deliverables:** integrated workflows; API client; environment configuration; integration notes.

**Exit gate:** Users can trace a site summary to underlying readings without mislabeled fixtures or stale data.

## Phase 12 — ESP32 and sensor integration

**Goal:** Connect actual hardware after sensors and pin map are verified.

**Work:** Establish a minimal I²C scan/chip-ID sketch. Resolve BME680 power, common ground, SDA/SCL, CS and SDO/address using board labels and measurements. The recent `Offline` output makes this an open hardware dependency, not by itself proof of a backend-code defect. Verify BME680 independently: scan at `0x76` or `0x77`, confirm ID `0x61`, obtain stable temperature/humidity/pressure/gas-resistance readings, and document observed address/wiring. For I²C, set CS for I²C mode as specified by the breakout. Verify analog sensor separately: output, ESP32 ADC pin, divider values, max ADC voltage, warm-up and safe range; ESP32 GPIO is not 5-V tolerant. Resolve actual MQ-135 pin against code; prior snippets disagreed about whether MQ-3/MQ-135 use GPIO34/35. Add device timestamp/sequence, validity flags and firmware version. Buffer/retry safely during Wi-Fi loss, bound memory and secure provisioning/rotation. Send HTTPS telemetry to staging and trace it through storage to UI. Start with verified sensors; gate MQ-3 features until confirmed.

**Deliverables:** verified pinout/wiring record; sensor baseline results; firmware client; provisioning/recovery instructions; end-to-end staging evidence.

**Exit gate:** Each sensor passes bench checks and real telemetry reaches storage/UI with correct units, identity, mode and freshness. If hardware is unresolved, explicit simulation remains usable while diagnosis continues.

## Phase 13 — Cleaning operations and evidence workflow

**Goal:** Turn alerts into accountable work without overstating sensor evidence.

**Work:** Implement task create/assign/due date/start/complete/cancel and audit transitions; validate transitions server-side. Record worker, washroom, linked task/incident, start/end, notes and optional evidence. Capture readings and score before/after with timestamps and engine version where available. Show “sensor-based response observed” or “no expected change observed,” with quality/timing caveats. Human task completion remains possible when telemetry is absent, with verification marked unavailable. Do not claim microbiological cleanliness or proof based only on sensor movement.

**Deliverables:** task/event APIs and UI; state transitions; before/after timeline; audit trail.

**Exit gate:** Cleaning is traceable from incident/task to completion and available sensor evidence, including honest offline cases.

## Phase 14 — Analytics and operations views

**Goal:** Support facility decisions from history.

**Work:** Implement time-series aggregation by washroom/site, sensor, score, alerts and cleaning response. Include 30-minute, 1-hour, 24-hour, 7-day and custom windows where volume allows. Define missing-data behavior and distinguish observations from interpolated/aggregated values; never fill gaps invisibly. Add filters/comparison/export subject to access policy. Track expected versus received telemetry. Provide system/device health for API/database/telemetry latency, request failures, ingestion errors and last seen, with admin-only access as appropriate.

**Deliverables:** analytics endpoints; charts/tables; device/system health views; export policy.

**Exit gate:** Aggregates reconcile to source data and gaps/stale intervals remain visible.

## Phase 15 — Security, reliability and quality assurance

**Goal:** Validate the complete system, including failure behavior.

**Work:** Unit-check normalization, sensor validity, scoring, classification, causes, alert deduplication, task transitions, auth and idempotency. API-check login/refresh/logout, wrong roles, cross-organization access, malformed/missing fields, unauthorized devices, bad timestamps and pagination. Integration-check device/simulator → API → PostgreSQL → engine → dashboard, including retries/duplicates. Exercise Wi-Fi/device outage, missing sensor, invalid range, BME startup failure, stale timestamps, database unavailable, API restart, expired token, failed notification and recovery. Verify no synthetic values appear as live. Review OWASP API risks: object authorization, sessions, data exposure, resource consumption and misconfiguration. Apply HTTPS, secure headers, restrictive CORS, rate limits, secret management, dependency updates and backups. Observe request/ingestion latency, telemetry lag, failures, errors, DB health and score failures; set thresholds and retention.

**Deliverables:** automated suite; security checklist; failure/recovery evidence; backup/restore procedure; release issues list.

**Exit gate:** Critical journeys/failures are covered, authorization is server-side and operators can identify degraded service/data.

## Phase 16 — Deployment and observability

**Goal:** Deploy a production-like system with secure configuration and recovery.

**Work:** Deploy frontend, FastAPI and PostgreSQL to Render or selected host, with separate dev/staging/production environments and domains. Require HTTPS for browser/device traffic. Store secrets only in host secret settings; never in frontend bundles, firmware examples, logs or Git. Configure migrations as a controlled release step, health/readiness, backups, log retention, resource limits, monitoring and error reporting. Establish GitHub CI for formatting/type checks/build/API checks and reviewed deployment. Document rollback/restore. Test real-device connection from target network and ESP32 certificate/time/network constraints.

**Deliverables:** deployed environments; CI/CD; HTTPS; monitoring; secrets/deployment guide; backup/rollback instructions.

**Exit gate:** Deployment is reproducible, monitored, backed up and reversible without obscuring live/simulation status.

## Phase 17 — Documentation, demo and release

**Goal:** Make the product operable and keep claims aligned with evidence.

**Work:** Write user guides for dashboard interpretation, alerts, cleaning tasks, device status and simulation. Write admin guides for users/roles, thresholds, washroom/device provisioning and credential rotation. Write developer/operator guides for local setup, migrations, API, firmware contract, environment variables, deployment, monitoring, troubleshooting and recovery. Prepare simulation demo scenarios and a separate live-hardware checklist. Review paper, UI copy and release notes for unsupported claims. Document calibration limitations and difference between heuristic score and validated hygiene measurement.

**Deliverables:** user/admin/developer/operator docs; demo script; release checklist; known limitations and calibration roadmap.

**Exit gate:** A new operator can set up a site/device and interpret a score without undocumented assumptions or mistaking simulation for hardware.

## Cross-phase acceptance criteria

- Login, password reset, role-aware access and audit trail for sensitive actions.
- Create/manage washrooms and register/manage devices.
- Receive authenticated telemetry, validate/store raw observations and trace derived records.
- Display freshness, live/simulation mode, device/sensor health and missing data.
- Produce versioned score/classification/cause indicators and alerts from approved rules.
- Acknowledge/resolve incidents and create/assign/start/complete cleaning tasks with traceable timelines.
- Show history and analytics over defined periods with visible gaps and units.
- Handle offline devices, Wi-Fi loss, malformed data, missing sensors, duplicates, restart and DB/API failures safely.
- Provide responsive UI, deployment, automated checks, monitoring and recoverable backups.

## Key risks, decisions and mitigations

| Risk/decision | Why it matters | Response |
|---|---|---|
| BME680 currently reports offline | BME views/score inputs cannot be demonstrated live | Resolve wiring/address/chip ID independently; support missing state |
| Address/SDO notes conflict | Wrong address/mode prevents initialization | Measure actual address; record pin level; note usual Bosch selection |
| Firmware pin assignments conflict | Wrong ADC pin/divider corrupts values | Audit sketch and wiring; publish verified pin map |
| MQ sensors lack calibration evidence | Score may be mistaken for concentration/validated hygiene | Store raw values/relative indices; version and label rules |
| Paper scope exceeds actual hardware | Demo may claim absent capabilities | Maintain per-device capability matrix; enable only verified features |
| 20-second simulation switch can mask outages | Synthetic values could appear current | Persistent mode/last-live time; tagged and isolated simulation |
| Existing app may already implement features | Rewrite risks loss of working code | Audit first; extend incrementally |
| Cleaning verification overclaims | Sensor response cannot prove pathogens removed | Separate human completion from sensor-based response evidence |

## Recommended execution order and dependencies

1. Start Phase 0: audit, requirements ledger and hardware baseline investigation. Do not overwrite the existing repository.
2. Run Phases 1–3 to make the 20 screens reviewable with explicit simulation fixtures. This creates a demonstrable product while hardware is repaired.
3. In parallel, agree the API/data contract (Phase 5) and actual device capability. Begin backend implementation after UX prototype and contracts are reviewable.
4. Build backend, access control, device registry and ingestion (Phases 6–8); then versioned rules and simulation (Phases 9–10).
5. Integrate frontend (Phase 11), then connect verified hardware (Phase 12). Hardware diagnosis gates live-sensor claims but not UI/simulation development.
6. Complete cleaning and analytics (Phases 13–14), then harden, deploy and document (Phases 15–17).

Calendar estimates depend on existing code, team size, hosting and sensor repair. Estimate after Phase 0. Contract design, UI review, test fixtures and hardware diagnosis can overlap; dependencies such as agreed telemetry schema before firmware integration should remain sequential.

## First concrete work package

1. Inspect and map existing repo; identify frontend/backend/simulator functionality.
2. Create requirements ledger and capability matrix: feature, screen/API, hardware source, status, phase and acceptance evidence.
3. Verify BME680 separately with I²C scan/chip ID; verify MQ-135 pin/divider; mark MQ-3 unavailable until confirmed.
4. Draft 20-screen sitemap and role/action matrix, then low-fidelity wireframes.
5. Build clickable UI with labelled fixtures and review it with the project owner.
6. Freeze telemetry/API contracts and scoring vocabulary before backend/ESP32 integration.

This sequence avoids silently assuming the BME680 is connected, treating uncalibrated MQ values as ppm, or presenting simulation as live data.
