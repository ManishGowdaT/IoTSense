from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Organization(TimestampMixin, Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")


class Facility(TimestampMixin, Base):
    __tablename__ = "facilities"
    __table_args__ = (Index("ix_facilities_organization_id", "organization_id"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")
    address: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email_normalized", name="uq_users_email_normalized"),
        Index("ix_users_organization_id", "organization_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    email_normalized: Mapped[str] = mapped_column(String(254), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="invited")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserSession(Base):
    __tablename__ = "user_sessions"
    __table_args__ = (Index("ix_user_sessions_user_expires", "user_id", "expires_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    csrf_token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = (Index("ix_password_reset_tokens_user_expires", "user_id", "expires_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    purpose: Mapped[str] = mapped_column(String(24), nullable=False, default="password_reset")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Washroom(TimestampMixin, Base):
    __tablename__ = "washrooms"
    __table_args__ = (
        Index("ix_washrooms_facility_id", "facility_id"),
        Index("ix_washrooms_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    facility_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("facilities.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    location_label: Mapped[str | None] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")
    capability_state: Mapped[str] = mapped_column(String(24), nullable=False, default="unverified")


class Device(TimestampMixin, Base):
    __tablename__ = "devices"
    __table_args__ = (
        UniqueConstraint("device_key_hash", name="uq_devices_device_key_hash"),
        Index("ix_devices_washroom_id", "washroom_id"),
        Index("ix_devices_status_last_seen", "status", "last_seen_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    washroom_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("washrooms.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    device_key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="unknown")
    firmware_version: Mapped[str | None] = mapped_column(String(64))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    key_rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Sensor(TimestampMixin, Base):
    __tablename__ = "sensors"
    __table_args__ = (
        UniqueConstraint("device_id", "sensor_key", name="uq_sensors_device_sensor_key"),
        Index("ix_sensors_device_id", "device_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False
    )
    sensor_key: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    sensor_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="unverified")
    interface_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    calibration_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"
    __table_args__ = (
        UniqueConstraint("device_id", "sequence", name="uq_telemetry_device_sequence"),
        Index("ix_telemetry_device_observed", "device_id", "observed_at"),
        Index("ix_telemetry_received_at", "received_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    firmware_version: Mapped[str] = mapped_column(String(64), nullable=False)
    source_mode: Mapped[str] = mapped_column(String(24), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    validation_result: Mapped[str] = mapped_column(String(24), nullable=False, default="accepted")


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    __table_args__ = (
        Index("ix_sensor_readings_sensor_observed", "sensor_id", "observed_at"),
        Index("ix_sensor_readings_metric_observed", "metric", "observed_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    telemetry_event_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("telemetry_events.id", ondelete="RESTRICT"), nullable=False
    )
    sensor_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("sensors.id", ondelete="RESTRICT")
    )
    sensor_key: Mapped[str] = mapped_column(String(64), nullable=False)
    metric: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    normalized_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    unit: Mapped[str] = mapped_column(String(24), nullable=False)
    quality: Mapped[str] = mapped_column(String(24), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class HygieneScore(Base):
    __tablename__ = "hygiene_scores"
    __table_args__ = (
        Index("ix_hygiene_scores_washroom_calculated", "washroom_id", "calculated_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    washroom_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("washrooms.id", ondelete="RESTRICT"), nullable=False
    )
    value: Mapped[int | None] = mapped_column(Integer)
    classification: Mapped[str] = mapped_column(String(24), nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(64), nullable=False)
    quality: Mapped[str] = mapped_column(String(24), nullable=False)
    source_mode: Mapped[str] = mapped_column(String(24), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    explanation: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)


class ScoreInput(Base):
    __tablename__ = "score_inputs"
    __table_args__ = (
        UniqueConstraint("hygiene_score_id", "sensor_reading_id", name="uq_score_inputs_pair"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    hygiene_score_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("hygiene_scores.id", ondelete="RESTRICT"), nullable=False
    )
    sensor_reading_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("sensor_readings.id", ondelete="RESTRICT"), nullable=False
    )
    contribution: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    explanation: Mapped[str | None] = mapped_column(Text)


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        Index("ix_incidents_washroom_status", "washroom_id", "status"),
        Index("ix_incidents_opened_at", "opened_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    washroom_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("washrooms.id", ondelete="RESTRICT"), nullable=False
    )
    incident_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    severity: Mapped[str] = mapped_column(String(24), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="open")
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deduplication_key: Mapped[str | None] = mapped_column(String(200))
    evidence_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    evidence_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_mode: Mapped[str] = mapped_column(String(24), nullable=False)


class AlertEvent(Base):
    __tablename__ = "alert_events"
    __table_args__ = (Index("ix_alert_events_incident_occurred", "incident_id", "occurred_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("incidents.id", ondelete="RESTRICT"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT")
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class CleaningTask(TimestampMixin, Base):
    __tablename__ = "cleaning_tasks"
    __table_args__ = (
        Index("ix_cleaning_tasks_washroom_status", "washroom_id", "status"),
        Index("ix_cleaning_tasks_assignee_status", "assignee_user_id", "status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    washroom_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("washrooms.id", ondelete="RESTRICT"), nullable=False
    )
    incident_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("incidents.id", ondelete="RESTRICT")
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="assigned")
    assignee_user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT")
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CleaningEvent(Base):
    __tablename__ = "cleaning_events"
    __table_args__ = (Index("ix_cleaning_events_task_occurred", "task_id", "occurred_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("cleaning_tasks.id", ondelete="RESTRICT"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT")
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text)
    evidence_reference: Mapped[str | None] = mapped_column(String(500))


class DeviceEvent(Base):
    __tablename__ = "device_events"
    __table_args__ = (Index("ix_device_events_device_occurred", "device_id", "occurred_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    device_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(48), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_organization_occurred", "organization_id", "occurred_at"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    actor_user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT")
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(100))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    outcome: Mapped[str] = mapped_column(String(24), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class NotificationPreference(TimestampMixin, Base):
    __tablename__ = "notification_preferences"
    __table_args__ = (
        Index("ix_notification_preferences_organization", "organization_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False
    )
    user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT")
    )
    channels: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    event_preferences: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    quiet_hours: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
