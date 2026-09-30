# Phase 9 — Versioned hygiene, cause and alert rules

**Status:** Conservative pure rule core added; persistence, approved policy and acceptance review remain open.

## Rule contract

The first engine is named `hygiene-v1`. It consumes observations with source quality, unit, timestamp and sensor calibration metadata, and returns an explainable evaluation with algorithm version, source observation IDs, quality, score/classification, indicator wording and an optional alert candidate.

- Only a fresh `mq135` `relative_index` observation with quality `valid`, unit `1`, and explicit calibration anchors `baseline_index < attention_index` can contribute.
- MQ-135 ADC counts, uncalibrated readings, MQ-3, BME680 temperature/humidity/pressure, stale readings and invalid or missing values do not contribute to a score.
- The relative response maps linearly from baseline (0 risk) to attention anchor (100 risk), clamped to that range. Where an explicitly supplied `ScoreBands` policy is absent, the engine returns `score=null` and `classification=unknown`. Score bands therefore cannot become active by accident.
- When configured, the heuristic indicator is `100 - mean(relative risk)`. This has not been validated as a hygiene measurement and must be labeled a rule-based estimate.
- A cause indicator says only that a calibrated MQ-135 relative index is above its own baseline. It is not a confirmed environmental or biological cause.
- An alert candidate requires an explicit per-sensor `alert_index` and `alert_severity`, no open alert, and an expired cooldown. Its deterministic key includes the triggering observation ID for retry idempotency.
- The pure function does not persist scores, alerts, score inputs or audit changes. The API has not yet wired or exposed this engine.

## Expected rule examples

With calibration anchors `baseline_index=10`, `attention_index=30`, and illustrative score bands `clean_min=80`, `moderate_min=50`:

| Input | Expected outcome |
|---|---|
| No observation, or only stale/missing/invalid input | No score; `unknown`; no alert |
| Valid relative index 10 | Score 100; `clean` under the supplied illustrative bands |
| Valid relative index 20 | Score 50; `moderate`; low-confidence baseline indicator |
| Valid relative index 40 with alert index 40 and explicit severity | Alert candidate if cooldown/open-alert checks allow |
| `analog_raw`, MQ-3 or BME680-only observations | Excluded; no score |
| Valid observation but no configured score bands | No score; `unknown` with explanation |

These values demonstrate arithmetic only. They are not recommended thresholds or product settings.

## Remaining decisions and work

- Define and review a reference calibration process and per-device anchor provenance/version before assigning anchors.
- Decide and approve score bands, sensor freshness windows, alert thresholds, severities, cooldowns and deduplication lifecycle.
- Persist configuration versions and audit threshold changes.
- Connect the evaluator to telemetry persistence so each derived record links to exact raw inputs, flags and engine version; implement idempotent alert create/acknowledge/resolve APIs.
- Add automated fixtures and run them with the backend dependency set, then review score/cause language before exposing it in the UI.
- Do not enable MQ-3, cleaning bonuses or BME680-derived score contributions without verified hardware and reviewed evidence.
