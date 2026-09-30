# IoTSense MVP

React dashboard for a stakeholder walkthrough or a direct ESP32 sensor demo. It can show its sample fixtures without backend services, or read MQ-3 and MQ-135 values over USB serial. The unavailable BME680 is represented by clearly labeled simulated values.

## Run locally

Requirements: Node.js 20.19+ or 22.12+ and npm.

```powershell
cd IoTSense\frontend
npm install
npm run demo
```

This builds the static demo bundle and serves it locally. Open the URL printed by Vite and navigate directly to `/app/dashboard` for the stakeholder walkthrough. If port 4173 is already in use, Vite prints another port; use that port instead.

Use `npm run demo` to build and serve the app. It does not start PostgreSQL, Docker, or the Python API.

## Connect an ESP32

1. Install the Arduino IDE and the ESP32 board support package.
2. Open `firmware/esp32/IoTSenseLive.ino`, choose your ESP32 board and USB port, then upload it. The sketch uses GPIO 34 for MQ-3 AO and GPIO 35 for MQ-135 AO; change `MQ3_PIN` and `MQ135_PIN` in the sketch if your wiring differs.
3. Power the MQ sensor modules as their boards require and connect grounds together. Connect each analog output to its configured ESP32 pin. Keep ESP32 ADC input at or below 3.3 V; use a voltage divider if a module's analog output can exceed that.
4. Run `npm run demo` in `frontend`, open the app in Chrome or Edge at the localhost URL, and click **Connect ESP32**. Select the ESP32 USB serial port. The first device is assigned to **Main building · North Wing · Washroom 1**. The dashboard reads both JSON telemetry from the supplied sketch and the readable text output from the alternate BME680 test sketch. MQ raw ADC readings appear with live BME680 values when available; otherwise the dashboard supplies labeled simulated temperature, humidity, pressure and gas resistance.

Close Arduino Serial Monitor and Serial Plotter before connecting from the browser; only one app can open the USB serial port at a time. If the browser says it failed to open the port, close those Arduino windows and select the ESP32 port again. The washroom detail and analysis views show raw counts, voltage-divider calculations, ADC range use, environmental values, source labels and recent readings. MQ readings are not calibrated gas concentration or ppm. The MVP score is an estimate using the tunable default ranges below; simulated BME680 values are marked in the dashboard and score panel.

## MVP hygiene score

The connected washroom uses the formula requested for the prototype: `Dirty Index = 0.5 × normalized MQ-135 + 0.5 × normalized BME680 VOC`, then `Raw Score = 100 − Dirty Index × 100`. If normalized MQ-3 is at least 0.6 and humidity rises by at least 0.15 percentage points from the previous serial reading, the score gets a 10 point cleaning bonus, capped at 100. Scores of 80–100 are Clean, 50–79 Moderate, and below 50 Dirty. A Dirty result creates an in-app cleaning alert.

Initial normalization ranges are in `src/features/live/hygiene.ts`: MQ-135 300–1800 ADC, MQ-3 300–1500 ADC, and BME680 gas resistance 10–150 kΩ, with lower gas resistance mapped to higher VOC response. These are tunable demo defaults, not validated sensor calibration. The app identifies simulated BME680 values in the score panel. The calculation runs in the browser and is not persisted to the backend.

## Prototype navigation

The left navigation exposes the workspace, management and account views. The Landing page links to Login; Login links to Forgot Password and the sample workspace. On Dashboard, the scenario selector demonstrates Normal, Moderate, Dirty, Cleaning, Recovery, Sensor Failure and Device Offline states. Search, alert acknowledgement, task start/completion, filters and prototype forms include local-only interactions.

Without a connected ESP32, the application shows illustrative sample fixtures. USB serial readings are held in the browser session and are not saved to the backend or database. Device credentials and authenticated telemetry transport are not part of this direct-to-browser MVP.
