"""Conservative, explainable hygiene indicator rules (hygiene-v1).

This module intentionally does not treat raw MQ ADC counts, uncalibrated values,
temperature, humidity, pressure, or MQ-3 readings as evidence of cleanliness.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

ENGINE_VERSION = "hygiene-v1"
Classification = Literal["clean", "moderate", "dirty", "unknown"]


@dataclass(frozen=True)
class Observation:
    id: UUID
    sensor_key: str
    metric: str
    value: float | None
    unit: str
    quality: str
    observed_at: datetime
    calibration_metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ScoreBands:
    """Classification cutoffs; callers must supply explicitly approved values."""

    clean_min: int
    moderate_min: int

    def __post_init__(self) -> None:
        if not (0 <= self.moderate_min <= self.clean_min <= 100):
            raise ValueError("Score bands must satisfy 0 <= moderate_min <= clean_min <= 100.")


@dataclass(frozen=True)
class RuleConfig:
    stale_after_seconds: int = 300
    score_bands: ScoreBands | None = None
    alert_cooldown_seconds: int = 900

    def __post_init__(self) -> None:
        if self.stale_after_seconds < 1 or self.alert_cooldown_seconds < 0:
            raise ValueError("Freshness must be positive and alert cooldown cannot be negative.")


@dataclass(frozen=True)
class CauseIndicator:
    key: str
    label: str
    evidence_observation_id: UUID
    observed_at: datetime
    quality: str
    confidence: Literal["low"] = "low"


@dataclass(frozen=True)
class AlertCandidate:
    deduplication_key: str
    severity: Literal["low", "medium", "high"]
    title: str
    evidence_observation_id: UUID
    evidence_start: datetime
    evidence_end: datetime


@dataclass(frozen=True)
class Evaluation:
    algorithm_version: str
    score: int | None
    classification: Classification
    quality: str
    explanation: tuple[str, ...]
    causes: tuple[CauseIndicator, ...]
    alert: AlertCandidate | None
    input_observation_ids: tuple[UUID, ...]


def _calibration_number(metadata: dict[str, object], key: str) -> float | None:
    value = metadata.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _fresh(observation: Observation, now: datetime, window: timedelta) -> bool:
    if observation.observed_at.tzinfo is None or observation.observed_at.utcoffset() is None:
        return False
    age = now - observation.observed_at.astimezone(UTC)
    return timedelta(0) <= age <= window


def evaluate(
    *,
    washroom_id: UUID,
    observations: list[Observation],
    now: datetime | None = None,
    config: RuleConfig = RuleConfig(),
    has_open_alert: bool = False,
    last_alert_at: datetime | None = None,
) -> Evaluation:
    """Evaluate MQ-135 relative-index evidence without claiming hygiene proof.

    A usable index requires quality `valid` and sensor calibration metadata with
    `baseline_index` and `attention_index`. Classification needs explicit bands.
    An alert additionally needs an `alert_index` and explicit `alert_severity`.
    """
    evaluated_at = now or datetime.now(UTC)
    if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
        raise ValueError("Evaluation time must include a timezone.")
    evaluated_at = evaluated_at.astimezone(UTC)
    fresh_window = timedelta(seconds=config.stale_after_seconds)
    explanations: list[str] = []
    usable: list[tuple[Observation, float, float, float]] = []
    ignored = 0

    for reading in observations:
        if reading.sensor_key != "mq135" or reading.metric != "relative_index":
            ignored += 1
            continue
        if reading.quality != "valid" or reading.value is None or not math.isfinite(reading.value):
            explanations.append(f"MQ-135 observation {reading.id} is not valid numeric evidence.")
            continue
        if reading.unit != "1" or not _fresh(reading, evaluated_at, fresh_window):
            explanations.append(f"MQ-135 observation {reading.id} has an unsupported unit or is stale.")
            continue
        baseline = _calibration_number(reading.calibration_metadata, "baseline_index")
        attention = _calibration_number(reading.calibration_metadata, "attention_index")
        if baseline is None or attention is None or attention <= baseline:
            explanations.append(f"MQ-135 observation {reading.id} has no usable calibration anchors.")
            continue
        alert_level = _calibration_number(reading.calibration_metadata, "alert_index")
        risk = min(100.0, max(0.0, (reading.value - baseline) / (attention - baseline) * 100.0))
        usable.append((reading, baseline, attention, risk))

    input_ids = tuple(item[0].id for item in usable)
    causes: list[CauseIndicator] = []
    alert: AlertCandidate | None = None
    score: int | None = None
    classification: Classification = "unknown"
    quality = "missing"

    if usable:
        quality = "valid"
        avg_risk = sum(item[3] for item in usable) / len(usable)
        causes = [
            CauseIndicator(
                key="mq135_relative_index_elevated",
                label="MQ-135 relative index is above its calibrated baseline",
                evidence_observation_id=reading.id,
                observed_at=reading.observed_at.astimezone(UTC),
                quality=reading.quality,
            )
            for reading, baseline, _, _ in usable
            if reading.value is not None and reading.value > baseline
        ]
        if config.score_bands is None:
            explanations.append("Score classification is disabled until score bands are explicitly configured.")
        else:
            score = round(100.0 - avg_risk)
            if score >= config.score_bands.clean_min:
                classification = "clean"
            elif score >= config.score_bands.moderate_min:
                classification = "moderate"
            else:
                classification = "dirty"

        for reading, _, _, _ in usable:
            alert_level = _calibration_number(reading.calibration_metadata, "alert_index")
            severity = reading.calibration_metadata.get("alert_severity")
            if (
                alert is None
                and alert_level is not None
                and reading.value is not None
                and reading.value >= alert_level
                and severity in {"low", "medium", "high"}
                and not has_open_alert
                and (last_alert_at is None or evaluated_at - last_alert_at.astimezone(UTC) >= timedelta(seconds=config.alert_cooldown_seconds))
            ):
                alert = AlertCandidate(
                    deduplication_key=f"{ENGINE_VERSION}:{washroom_id}:mq135:{reading.id}",
                    severity=severity,
                    title="Calibrated MQ-135 relative index exceeded its alert level",
                    evidence_observation_id=reading.id,
                    evidence_start=reading.observed_at.astimezone(UTC),
                    evidence_end=reading.observed_at.astimezone(UTC),
                )
                break
    else:
        explanations.append("No fresh, valid, calibrated MQ-135 relative-index observation is available.")

    if ignored:
        explanations.append(f"{ignored} unsupported or non-MQ-135 observation(s) were excluded from this rule.")
    explanations.append("This rule reports sensor indicators only; it does not establish cleanliness or pathogen presence.")
    return Evaluation(
        algorithm_version=ENGINE_VERSION,
        score=score,
        classification=classification,
        quality=quality,
        explanation=tuple(explanations),
        causes=tuple(causes),
        alert=alert,
        input_observation_ids=input_ids,
    )
