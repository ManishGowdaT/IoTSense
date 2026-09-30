from __future__ import annotations

import hashlib
import json
import math
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models import Device, Sensor, SensorReading, TelemetryEvent

router = APIRouter(tags=["Telemetry"])
legacy_router = APIRouter(tags=["Telemetry"])

QUALITY_VALUES = {"valid", "stale", "missing", "invalid", "warming_up", "uncalibrated"}
UNIT_BY_METRIC = {
    "temperature_c": "Cel",
    "relative_humidity_pct": "%",
    "pressure_pa": "Pa",
    "gas_resistance_ohm": "Ohm",
    "analog_raw": "count",
    "pin_voltage_v": "V",
    "relative_index": "1",
}
METRIC_LIMITS: dict[str, tuple[float, float]] = {
    "temperature_c": (-40, 85),
    "relative_humidity_pct": (0, 100),
    "pressure_pa": (30_000, 120_000),
    "gas_resistance_ohm": (0.000001, 1_000_000_000),
    "analog_raw": (0, 65_535),
    "pin_voltage_v": (0, 3.6),
    "relative_index": (-1_000_000_000_000, 1_000_000_000_000),
}


def _problem(status_code: int, code: str, title: str, detail: str) -> HTTPException:
    return HTTPException(status_code, detail={"code": code, "title": title, "detail": detail})


class TelemetryObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sensor_key: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.:-]+$")
    metric: str = Field(pattern=r"^(temperature_c|relative_humidity_pct|pressure_pa|gas_resistance_ohm|analog_raw|pin_voltage_v|relative_index)$")
    value: float | None
    unit: str = Field(min_length=1, max_length=24)
    quality: str = "valid"
    metadata: dict[str, object] = Field(default_factory=dict, max_length=32)

    @field_validator("value")
    @classmethod
    def finite_value(cls, value: float | None) -> float | None:
        if value is not None and not math.isfinite(value):
            raise ValueError("Value must be finite.")
        return value

    @field_validator("metadata")
    @classmethod
    def bounded_json_metadata(cls, value: dict[str, object]) -> dict[str, object]:
        try:
            encoded = json.dumps(value, allow_nan=False, separators=(",", ":"))
        except (TypeError, ValueError, RecursionError) as exc:
            raise ValueError("Metadata must contain finite JSON values.") from exc
        if len(encoded.encode("utf-8")) > 4096:
            raise ValueError("Metadata exceeds 4096 bytes.")
        return value

    @model_validator(mode="after")
    def validate_metric_value(self) -> TelemetryObservation:
        if self.quality not in QUALITY_VALUES:
            raise ValueError("Unsupported quality value.")
        if UNIT_BY_METRIC[self.metric] != self.unit:
            raise ValueError(f"Expected unit {UNIT_BY_METRIC[self.metric]} for {self.metric}.")
        if self.quality == "missing":
            if self.value is not None:
                raise ValueError("Missing observations must use a null value.")
            return self
        if self.value is None:
            raise ValueError("Only missing observations may use a null value.")
        lower, upper = METRIC_LIMITS[self.metric]
        if not lower <= self.value <= upper:
            raise ValueError("Value is outside the accepted input range.")
        return self


class TelemetryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: UUID | None = None
    sequence: int = Field(ge=0, le=2_147_483_647)
    observed_at: datetime
    firmware_version: str = Field(min_length=1, max_length=64)
    observations: list[TelemetryObservation] = Field(max_length=64)

    @field_validator("observed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must include a timezone.")
        return value.astimezone(UTC)

    @field_validator("firmware_version")
    @classmethod
    def nonblank_firmware(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Firmware version cannot be blank.")
        return value


class TelemetryReceipt(BaseModel):
    telemetry_event_id: UUID
    device_id: UUID
    sequence: int
    received_at: datetime
    source_mode: str
    duplicate: bool


def _device_for_key(db: Session, raw_key: str | None) -> Device:
    if not raw_key or len(raw_key) < 32 or len(raw_key) > 256:
        raise _problem(401, "device_authentication_required", "Device authentication required", "A valid device credential is required.")
    digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    device = db.scalar(select(Device).where(Device.device_key_hash == digest))
    if device is None or device.revoked_at is not None:
        raise _problem(401, "invalid_device_credential", "Device authentication failed", "A valid device credential is required.")
    return device


def _payload_hash(payload: TelemetryRequest) -> str:
    canonical = payload.model_dump(mode="json", exclude={"device_id"})
    canonical["observed_at"] = payload.observed_at.isoformat().replace("+00:00", "Z")
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _receipt(event: TelemetryEvent, duplicate: bool) -> TelemetryReceipt:
    return TelemetryReceipt(
        telemetry_event_id=event.id, device_id=event.device_id,
        sequence=event.sequence, received_at=event.received_at,
        source_mode=event.source_mode, duplicate=duplicate,
    )


def _accept_telemetry(payload: TelemetryRequest, x_device_key: str | None, db: Session) -> TelemetryReceipt:
    device = _device_for_key(db, x_device_key)
    if payload.device_id is not None and payload.device_id != device.id:
        raise _problem(403, "device_identity_mismatch", "Device identity mismatch", "The payload device ID does not match its credential.")
    now = datetime.now(UTC)
    settings = get_settings()
    if payload.observed_at > now + timedelta(seconds=settings.telemetry_max_clock_skew_seconds):
        raise _problem(422, "timestamp_in_future", "Invalid observation time", "The observation timestamp is too far in the future.")
    if payload.observed_at < now - timedelta(seconds=settings.telemetry_max_past_age_seconds):
        raise _problem(422, "timestamp_too_old", "Invalid observation time", "The observation timestamp is outside the accepted replay window.")
    payload_hash = _payload_hash(payload)
    existing = db.scalar(select(TelemetryEvent).where(
        TelemetryEvent.device_id == device.id, TelemetryEvent.sequence == payload.sequence
    ))
    if existing is not None:
        if existing.payload_hash != payload_hash:
            raise _problem(409, "idempotency_conflict", "Sequence already used", "This device sequence was already accepted with different content.")
        return _receipt(existing, duplicate=True)

    latest_sequence = db.scalar(select(TelemetryEvent.sequence).where(
        TelemetryEvent.device_id == device.id
    ).order_by(TelemetryEvent.sequence.desc()).limit(1))
    if latest_sequence is not None and payload.sequence <= latest_sequence:
        raise _problem(409, "sequence_out_of_order", "Sequence out of order", "New telemetry must use a sequence greater than the last accepted sequence.")

    event = TelemetryEvent(
        id=uuid4(), device_id=device.id, sequence=payload.sequence,
        observed_at=payload.observed_at, firmware_version=payload.firmware_version,
        source_mode="live_hardware", payload_hash=payload_hash, validation_result="accepted",
    )
    db.add(event)
    sensor_ids = {
        sensor.sensor_key: sensor.id
        for sensor in db.scalars(select(Sensor).where(Sensor.device_id == device.id))
    }
    for observation in payload.observations:
        db.add(SensorReading(
            id=uuid4(), telemetry_event_id=event.id,
            sensor_id=sensor_ids.get(observation.sensor_key),
            sensor_key=observation.sensor_key, metric=observation.metric,
            raw_value=Decimal(str(observation.value)) if observation.value is not None else None,
            normalized_value=None, unit=observation.unit, quality=observation.quality,
            observed_at=payload.observed_at, metadata_json=observation.metadata,
        ))
    device.last_seen_at = now
    device.firmware_version = payload.firmware_version
    device.status = "degraded" if any(o.quality in {"missing", "invalid"} for o in payload.observations) else "online"
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raced = db.scalar(select(TelemetryEvent).where(
            TelemetryEvent.device_id == device.id, TelemetryEvent.sequence == payload.sequence
        ))
        if raced is None:
            raise
        if raced.payload_hash != payload_hash:
            raise _problem(409, "idempotency_conflict", "Sequence already used", "This device sequence was already accepted with different content.")
        return _receipt(raced, duplicate=True)
    db.refresh(event)
    return _receipt(event, duplicate=False)


async def _guard_payload_size(request: Request) -> None:
    limit = get_settings().telemetry_max_payload_bytes
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > limit:
        raise _problem(413, "payload_too_large", "Payload too large", "The telemetry payload exceeds the accepted size.")
    if len(await request.body()) > limit:
        raise _problem(413, "payload_too_large", "Payload too large", "The telemetry payload exceeds the accepted size.")


@router.post("/api/v1/telemetry", status_code=status.HTTP_202_ACCEPTED, response_model=TelemetryReceipt)
async def ingest_telemetry(
    payload: TelemetryRequest,
    request: Request,
    x_device_key: str | None = Header(default=None, alias="X-Device-Key"),
    db: Session = Depends(get_db),
) -> TelemetryReceipt:
    await _guard_payload_size(request)
    return _accept_telemetry(payload, x_device_key, db)


@legacy_router.post("/api/ingest", status_code=status.HTTP_202_ACCEPTED, response_model=TelemetryReceipt, deprecated=True)
async def ingest_telemetry_compat(
    payload: TelemetryRequest,
    request: Request,
    x_device_key: str | None = Header(default=None, alias="X-Device-Key"),
    db: Session = Depends(get_db),
) -> TelemetryReceipt:
    await _guard_payload_size(request)
    return _accept_telemetry(payload, x_device_key, db)
