# Phase 0 — Greenfield project baseline

**Status:** Initial baseline created. Application implementation has not started.

## 1. Project intent

Create IoTSense as a web and IoT product for washroom condition monitoring and facility-management workflows. The intended data path is:

`ESP32 + sensors → authenticated HTTPS telemetry API → Python service → PostgreSQL → explainable indicators and alerts → React dashboard and cleaning workflows`

The product should support both live hardware and simulation, with an unmistakable label and timestamp for each mode.

## 2. Confirmed from the project conversation

- The user wants to build the software from scratch; there is no existing application repository to audit.
- The intended controller is an ESP32 Dev Module.
- A BME680 breakout is present in the project, but recent firmware output reports it as offline/not initialized. It is therefore **not currently verified as a working input**.
- MQ-135 has produced analog readings in a prior test. Its exact current GPIO and divider wiring need to be verified against the physical setup and final firmware.
- MQ-3 is not confirmed as connected or working. Do not build active product behavior that depends on it until verified.
- Earlier notes conflict about the BME680 I²C address and SDO level. Establish the address from an I²C scan and chip ID rather than assuming it.
- The supplied product prompt specifies 20 screens in its final inventory; that count is used as the baseline.
- Planned software stack: React/Vite/TypeScript frontend; Python/FastAPI backend; PostgreSQL; ESP32 firmware; Render as the proposed hosting target; GitHub for version control/automation.

## 3. Product truth and safety rules

- Treat MQ-135/MQ-3 readings as relative indices until calibrated against an appropriate reference. Do not claim exact ppm from these readings.
- Do not claim pathogen detection, medical diagnosis, certification, or definitive proof that a washroom is clean.
- Distinguish observed sensor readings, computed heuristic indicators and synthetic simulation values in storage, APIs, charts and UI.
- Missing, stale, invalid or disconnected sensors must produce an explicit unknown/degraded/offline state. Never replace missing live data with undisclosed synthetic values.
- Cleaning task completion is a human/operational event. Sensor movement can be shown as supporting evidence, not proof of microbiological cleanliness.
- Do not store credentials in source control, client-side code or public firmware examples.

## 4. Initial capability matrix

| Capability | Baseline status | Evidence needed before enabling live product behavior |
|---|---|---|
| ESP32 device | Intended hardware | Record exact board and verified pin labels |
| BME680 | Present but currently offline/unverified | I²C scan, chip ID `0x61`, stable readings and measured address |
| MQ-135 | Analog readings previously observed | Verify actual GPIO, output voltage, divider and repeatability |
| MQ-3 | Unconfirmed | Physical connection, independent readings and calibration/interpretation decision |
| Live telemetry to server | Not implemented | Device authentication and end-to-end staging delivery |
| Simulation | Not implemented | Tagged scenario data that cannot be confused with live readings |
| Web application | Not implemented | UI prototype and then integrated frontend |
| Backend/database | Not implemented | API contract, migrations and local service |

## 5. Initial repository structure

```text
IoTSense/
├── backend/                 # FastAPI service, migrations and backend tests
│   ├── app/
│   └── tests/
├── docs/
│   ├── phase-0/
│   ├── product/
│   ├── architecture/
│   ├── hardware/
│   └── operations/
├── firmware/
│   └── esp32/
├── frontend/                # React/Vite/TypeScript
├── infra/                   # Local and hosting configuration
├── tests/                   # Integration and end-to-end material
├── tools/                   # Development utilities
├── .env.example
├── .gitignore
└── README.md
```

Folders are created as a scaffold only. Dependencies and application code will be added in their planned phases rather than guessed now.

## 6. Initial decisions

| ID | Decision | Status |
|---|---|---|
| D-001 | Build a new IoTSense application in a dedicated project folder | Confirmed |
| D-002 | Preserve explicit Live Hardware and Simulation modes | Confirmed requirement |
| D-003 | Begin with UX/prototype before backend implementation | Planned; follows supplied prompt |
| D-004 | Use React/Vite/TypeScript, FastAPI and PostgreSQL as proposed stack | Planned; validate during setup |
| D-005 | Use a versioned, explainable heuristic engine before considering ML | Planned |
| D-006 | Treat BME680 address as unverified until scanned; Bosch SDO low normally selects `0x76`, high `0x77` | Hardware verification required |
| D-007 | Keep MQ readings relative until calibration supports stronger claims | Confirmed product constraint |
| D-008 | Extend this scaffold without replacing useful user work | Ongoing preservation rule |

## 7. Open questions and dependencies

These do not prevent creating the scaffold or beginning UX work:

1. Confirm actual BME680 wiring and address from a scan; recent reports show it offline.
2. Confirm exact MQ-135 GPIO and divider values. Older code snippets disagree on analog pin assignments.
3. Confirm whether MQ-3 is physically connected; otherwise mark it unavailable in release one.
4. Confirm initial deployment ownership/domain and whether Render remains the hosting target when deployment begins.
5. Decide the first release’s site/organization scale and data-retention period before production sizing.
6. Approve score thresholds and formulas only after the initial scoring specification is reviewed; prior paper formulas are not automatically validated.

## 8. Phase 0 exit criteria

- [x] Dedicated project folder and initial directory scaffold created.
- [x] Scope and product-truth constraints recorded.
- [x] Hardware capability matrix records verified versus unverified inputs.
- [x] Stack and major open decisions documented.
- [ ] Local development tools/runtime versions selected and recorded.
- [ ] Hardware pin/address record completed from measured evidence.
- [ ] Phase 1 screen sitemap and role/action matrix approved.

Phase 0 is intentionally not marked complete until the remaining setup choices and hardware facts are recorded. Hardware verification may proceed alongside Phase 1 UX work.
