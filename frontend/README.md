# IoTSense frontend prototype

Phase 3 clickable UI prototype built with React, TypeScript and Vite. It currently uses frontend fixtures only; there is no backend or hardware connection.

## Run locally

Requirements: Node.js 20.19+ or 22.12+ and npm.

```powershell
cd IoTSense\frontend
npm install
npm run dev
```

Open the local URL printed by Vite. To create a production bundle later, use `npm run build`.

## Prototype navigation

The left navigation exposes the workspace, management and account views. The Landing page links to Login; Login links to Forgot Password and the sample workspace. On Dashboard, the scenario selector demonstrates Normal, Moderate, Dirty, Cleaning, Recovery, Sensor Failure and Device Offline states. Search, alert acknowledgement, task start/completion, filters and prototype forms include local-only interactions.

All data is illustrative and is labeled as **Sample data**. No values are read from the ESP32, BME680, MQ sensors, API or database. Device credentials and user authentication are not implemented.
