#include <Arduino.h>
#include <math.h>

// IoTSense MVP serial bridge for ESP32 + MQ-3 + MQ-135.
// BME680 fields below are simulated and clearly marked in every JSON record.
// Change these pins to match your wiring. Use ADC1 pins so Wi-Fi is not required.
constexpr int MQ3_PIN = 34;
constexpr int MQ135_PIN = 35;
constexpr uint32_t REPORT_INTERVAL_MS = 1000;

uint32_t lastReport = 0;
uint32_t sequenceNumber = 0;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // ESP32 ADC: 0-4095
  pinMode(MQ3_PIN, INPUT);
  pinMode(MQ135_PIN, INPUT);
  delay(1200);
  Serial.println("{\"type\":\"iotsense_ready\",\"version\":\"0.1.0\"}");
}

void loop() {
  const uint32_t now = millis();
  if (now - lastReport < REPORT_INTERVAL_MS) return;
  lastReport = now;

  const int mq3Raw = analogRead(MQ3_PIN);
  const int mq135Raw = analogRead(MQ135_PIN);

  // Placeholder values for the unavailable BME680. A small deterministic drift
  // makes the dashboard visibly update without implying real measurements.
  const float phase = (sequenceNumber % 120) * 0.05236f;
  const float simulatedTempC = 25.0f + 1.2f * sinf(phase);
  const float simulatedHumidityPct = 55.0f + 4.0f * sinf(phase * 1.6f + 1.0f);
  const float simulatedPressureHpa = 1013.0f + 1.5f * sinf(phase * 0.4f);

  Serial.printf(
    "{\"type\":\"telemetry\",\"sequence\":%lu,\"uptime_ms\":%lu,"
    "\"mq3_raw\":%d,\"mq135_raw\":%d,\"temperature_c\":%.1f,"
    "\"humidity_pct\":%.1f,\"pressure_hpa\":%.1f,\"bme680_simulated\":true}\n",
    static_cast<unsigned long>(sequenceNumber++),
    static_cast<unsigned long>(now), mq3Raw, mq135Raw,
    simulatedTempC, simulatedHumidityPct, simulatedPressureHpa
  );
}
