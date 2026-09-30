# Phase 3 — Clickable UI prototype

**Status:** Prototype implementation created.

## Included

- React + TypeScript + Vite frontend scaffold.
- Navigable pages for the 20-screen inventory in the Phase 1 blueprint.
- Responsive app shell, workspace navigation, site selector and sample-data banner.
- Dashboard fixtures for Normal, Moderate, Dirty, Cleaning, Recovery, Sensor Failure and Device Offline scenarios.
- Washroom search, alert acknowledgement, cleaning task start/completion, prototype forms and cross-screen links for the main journeys.
- Illustrative charts, score explanations, sensor/device states, administrative tables and account screens.
- Explicit sample-data copy across pages. No simulated fixture is represented as an ESP32 reading.

## Prototype limits

- No API, database, authentication, device provisioning, telemetry ingestion or firmware connection is present yet.
- Actions are local UI demonstrations only; a refresh resets their state.
- Chart points and organization records are fixed fixtures. They are not calibrated sensor readings or validated hygiene measurements.
- Score bands and index values are illustrative and do not establish exact gas concentrations or cleanliness.
- The Landing, Login, Forgot Password and all authenticated workspace screens are accessible through the UI navigation flow.

## Phase 3 review checklist

- [x] 20-screen inventory represented in navigable frontend.
- [x] Sample data is disclosed in the application shell and footer.
- [x] Core alert-to-cleaning and status-to-analysis paths are clickable.
- [x] Missing, stale, offline and unknown states appear in fixtures.
- [x] Simulation scenario selector demonstrates key operating states.
- [x] Responsive layouts and keyboard focus styles are specified in the frontend.
- [ ] Review screen hierarchy, wording, scenario behavior and visual tokens with the project owner.
- [ ] After review, adjust prototype before moving into backend/API integration planning.
