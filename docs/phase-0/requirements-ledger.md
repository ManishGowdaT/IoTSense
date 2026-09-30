# IoTSense requirements ledger

Initial ledger derived from the supplied product prompt. “Planned” does not mean implemented.

| ID | Requirement | Category | Initial priority | Acceptance evidence |
|---|---|---|---|---|
| R-001 | Show multi-washroom operational dashboard | Product/UI | Release 1 | Dashboard summarizes washrooms, status, alerts and data freshness |
| R-002 | Provide 20 specified product/admin screens | Product/UI | Release 1, staged | Screen inventory and journeys reviewed; pages navigable |
| R-003 | Support Live Hardware and Simulation modes | Data integrity | Release 1 | Mode, source and last-live time are visible and stored |
| R-004 | Ingest authenticated ESP32 telemetry over HTTPS | Device/API | Release 1 | Authorized sample payload stored with provenance |
| R-005 | Store raw readings separately from derived indicators | Data | Release 1 | Derived records trace to source readings and engine version |
| R-006 | Produce hygiene score/classification | Analytics | Release 1, gated | Approved versioned rule spec and known-input examples |
| R-007 | Explain likely causes with cautious language | Analytics | Release 1, gated | Results include supporting inputs, time window and data quality |
| R-008 | Create, acknowledge and resolve alerts/incidents | Operations | Release 1 | Alert lifecycle and audit records demonstrated |
| R-009 | Manage cleaning tasks and events | Operations | Release 1 | Assign/start/complete workflow with traceable event history |
| R-010 | Present before/after sensor response carefully | Operations | Release 1, gated | Evidence includes timestamps/quality; no cleanliness guarantee |
| R-011 | Support four roles: Super Admin, Facility Admin, Maintenance Staff, Viewer | Security | Release 1 | Server-side authorization matrix exercised |
| R-012 | Manage devices, provisioning and device health | Device/API | Release 1 | Device identity, status, last seen and revocation supported |
| R-013 | Provide analytics over defined time ranges | Analytics | Release 1 | Aggregations reconcile to stored readings and show gaps |
| R-014 | Provide audit logs and system health views | Operations | Release 1 | Authorized admin can review changes and service/device health |
| R-015 | Make UI responsive and accessible | UI | Release 1 | Keyboard/focus/contrast and responsive review |
| R-016 | Handle missing, stale, invalid and offline sensor data honestly | Reliability | Release 1 | Failure scenarios show unknown/degraded/offline, not false clean |
| R-017 | Treat MQ values as relative until validated/calibrated | Product truth | Release 1 | UI/API/docs do not call values ppm without evidence |
| R-018 | Support BME680 environmental readings when hardware is verified | Hardware | Conditional | Scanner sees device, chip ID matches, stable readings captured |
| R-019 | Support MQ-3-dependent behavior only if sensor is verified | Hardware | Deferred/conditional | Physical input and interpretation are validated |
| R-020 | Deploy frontend, API and database with HTTPS and observability | Operations | Release 1 | Staging/prod deployment, health, backup and monitoring evidence |
| R-021 | Use simulation scenarios for demo and development | Simulation | Release 1 | Scenarios are tagged, repeatable and visually identified |
| R-022 | Document user, admin, developer and operations workflows | Documentation | Release 1 | Guides match shipped features and limitations |
