"""Create the initial IoTSense relational schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-30
"""

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def _execute_statements(script: str) -> None:
    for statement in script.split(";"):
        if statement.strip():
            op.execute(statement)


def upgrade() -> None:
    _execute_statements("""
    CREATE TABLE organizations (
        id UUID PRIMARY KEY, name VARCHAR(160) NOT NULL,
        status VARCHAR(24) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE TABLE facilities (
        id UUID PRIMARY KEY, organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
        name VARCHAR(160) NOT NULL, timezone VARCHAR(64) NOT NULL, address VARCHAR(500),
        status VARCHAR(24) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX ix_facilities_organization_id ON facilities(organization_id);
    CREATE TABLE users (
        id UUID PRIMARY KEY, organization_id UUID REFERENCES organizations(id) ON DELETE RESTRICT,
        email_normalized VARCHAR(254) NOT NULL, display_name VARCHAR(120) NOT NULL,
        password_hash VARCHAR(255), role VARCHAR(32) NOT NULL, status VARCHAR(24) NOT NULL,
        last_login_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_users_email_normalized UNIQUE(email_normalized)
    );
    CREATE INDEX ix_users_organization_id ON users(organization_id);
    CREATE TABLE washrooms (
        id UUID PRIMARY KEY, facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE RESTRICT,
        name VARCHAR(120) NOT NULL, location_label VARCHAR(160), status VARCHAR(24) NOT NULL,
        capability_state VARCHAR(24) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX ix_washrooms_facility_id ON washrooms(facility_id);
    CREATE INDEX ix_washrooms_status ON washrooms(status);
    CREATE TABLE devices (
        id UUID PRIMARY KEY, washroom_id UUID NOT NULL REFERENCES washrooms(id) ON DELETE RESTRICT,
        name VARCHAR(120) NOT NULL, device_key_hash VARCHAR(255) NOT NULL,
        status VARCHAR(24) NOT NULL, firmware_version VARCHAR(64), last_seen_at TIMESTAMPTZ,
        key_rotated_at TIMESTAMPTZ, revoked_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_devices_device_key_hash UNIQUE(device_key_hash)
    );
    CREATE INDEX ix_devices_washroom_id ON devices(washroom_id);
    CREATE INDEX ix_devices_status_last_seen ON devices(status, last_seen_at);
    CREATE TABLE sensors (
        id UUID PRIMARY KEY, device_id UUID NOT NULL REFERENCES devices(id) ON DELETE RESTRICT,
        sensor_key VARCHAR(64) NOT NULL, model VARCHAR(100) NOT NULL,
        sensor_type VARCHAR(64) NOT NULL, status VARCHAR(24) NOT NULL,
        interface_metadata JSON NOT NULL, calibration_metadata JSON NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_sensors_device_sensor_key UNIQUE(device_id, sensor_key)
    );
    CREATE INDEX ix_sensors_device_id ON sensors(device_id);
    CREATE TABLE telemetry_events (
        id UUID PRIMARY KEY, device_id UUID NOT NULL REFERENCES devices(id) ON DELETE RESTRICT,
        sequence INTEGER NOT NULL, observed_at TIMESTAMPTZ NOT NULL,
        received_at TIMESTAMPTZ NOT NULL DEFAULT now(), firmware_version VARCHAR(64) NOT NULL,
        source_mode VARCHAR(24) NOT NULL, payload_hash VARCHAR(64) NOT NULL,
        validation_result VARCHAR(24) NOT NULL,
        CONSTRAINT uq_telemetry_device_sequence UNIQUE(device_id, sequence)
    );
    CREATE INDEX ix_telemetry_device_observed ON telemetry_events(device_id, observed_at);
    CREATE INDEX ix_telemetry_received_at ON telemetry_events(received_at);
    CREATE TABLE sensor_readings (
        id UUID PRIMARY KEY,
        telemetry_event_id UUID NOT NULL REFERENCES telemetry_events(id) ON DELETE RESTRICT,
        sensor_id UUID REFERENCES sensors(id) ON DELETE RESTRICT,
        sensor_key VARCHAR(64) NOT NULL, metric VARCHAR(64) NOT NULL,
        raw_value NUMERIC(20,6), normalized_value NUMERIC(20,6), unit VARCHAR(24) NOT NULL,
        quality VARCHAR(24) NOT NULL, observed_at TIMESTAMPTZ NOT NULL,
        received_at TIMESTAMPTZ NOT NULL DEFAULT now(), metadata_json JSON NOT NULL
    );
    CREATE INDEX ix_sensor_readings_sensor_observed ON sensor_readings(sensor_id, observed_at);
    CREATE INDEX ix_sensor_readings_metric_observed ON sensor_readings(metric, observed_at);
    CREATE TABLE hygiene_scores (
        id UUID PRIMARY KEY, washroom_id UUID NOT NULL REFERENCES washrooms(id) ON DELETE RESTRICT,
        value INTEGER, classification VARCHAR(24) NOT NULL, algorithm_version VARCHAR(64) NOT NULL,
        quality VARCHAR(24) NOT NULL, source_mode VARCHAR(24) NOT NULL,
        calculated_at TIMESTAMPTZ NOT NULL, explanation JSON NOT NULL
    );
    CREATE INDEX ix_hygiene_scores_washroom_calculated ON hygiene_scores(washroom_id, calculated_at);
    CREATE TABLE score_inputs (
        id UUID PRIMARY KEY, hygiene_score_id UUID NOT NULL REFERENCES hygiene_scores(id) ON DELETE RESTRICT,
        sensor_reading_id UUID NOT NULL REFERENCES sensor_readings(id) ON DELETE RESTRICT,
        contribution NUMERIC(12,6), weight NUMERIC(12,6), explanation TEXT,
        CONSTRAINT uq_score_inputs_pair UNIQUE(hygiene_score_id, sensor_reading_id)
    );
    CREATE TABLE incidents (
        id UUID PRIMARY KEY, washroom_id UUID NOT NULL REFERENCES washrooms(id) ON DELETE RESTRICT,
        incident_type VARCHAR(64) NOT NULL, title VARCHAR(200) NOT NULL,
        severity VARCHAR(24) NOT NULL, status VARCHAR(24) NOT NULL, opened_at TIMESTAMPTZ NOT NULL,
        updated_at TIMESTAMPTZ, resolved_at TIMESTAMPTZ, deduplication_key VARCHAR(200),
        evidence_start TIMESTAMPTZ, evidence_end TIMESTAMPTZ, source_mode VARCHAR(24) NOT NULL
    );
    CREATE INDEX ix_incidents_washroom_status ON incidents(washroom_id, status);
    CREATE INDEX ix_incidents_opened_at ON incidents(opened_at);
    CREATE TABLE alert_events (
        id UUID PRIMARY KEY, incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE RESTRICT,
        event_type VARCHAR(32) NOT NULL,
        actor_user_id UUID REFERENCES users(id) ON DELETE RESTRICT,
        occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(), note TEXT, metadata_json JSON NOT NULL
    );
    CREATE INDEX ix_alert_events_incident_occurred ON alert_events(incident_id, occurred_at);
    CREATE TABLE cleaning_tasks (
        id UUID PRIMARY KEY, washroom_id UUID NOT NULL REFERENCES washrooms(id) ON DELETE RESTRICT,
        incident_id UUID REFERENCES incidents(id) ON DELETE RESTRICT,
        title VARCHAR(160) NOT NULL, status VARCHAR(24) NOT NULL,
        assignee_user_id UUID REFERENCES users(id) ON DELETE RESTRICT,
        due_at TIMESTAMPTZ, started_at TIMESTAMPTZ, completed_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX ix_cleaning_tasks_washroom_status ON cleaning_tasks(washroom_id, status);
    CREATE INDEX ix_cleaning_tasks_assignee_status ON cleaning_tasks(assignee_user_id, status);
    CREATE TABLE cleaning_events (
        id UUID PRIMARY KEY, task_id UUID NOT NULL REFERENCES cleaning_tasks(id) ON DELETE RESTRICT,
        event_type VARCHAR(32) NOT NULL,
        actor_user_id UUID REFERENCES users(id) ON DELETE RESTRICT,
        occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(), note TEXT, evidence_reference VARCHAR(500)
    );
    CREATE INDEX ix_cleaning_events_task_occurred ON cleaning_events(task_id, occurred_at);
    CREATE TABLE device_events (
        id UUID PRIMARY KEY, device_id UUID NOT NULL REFERENCES devices(id) ON DELETE RESTRICT,
        event_type VARCHAR(48) NOT NULL, occurred_at TIMESTAMPTZ NOT NULL, details JSON NOT NULL
    );
    CREATE INDEX ix_device_events_device_occurred ON device_events(device_id, occurred_at);
    CREATE TABLE audit_logs (
        id UUID PRIMARY KEY,
        organization_id UUID REFERENCES organizations(id) ON DELETE RESTRICT,
        actor_user_id UUID REFERENCES users(id) ON DELETE RESTRICT,
        action VARCHAR(100) NOT NULL, resource_type VARCHAR(80) NOT NULL, resource_id VARCHAR(100),
        occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(), outcome VARCHAR(24) NOT NULL,
        metadata_json JSON NOT NULL
    );
    CREATE INDEX ix_audit_logs_organization_occurred ON audit_logs(organization_id, occurred_at);
    CREATE INDEX ix_audit_logs_resource ON audit_logs(resource_type, resource_id);
    CREATE TABLE notification_preferences (
        id UUID PRIMARY KEY, organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
        user_id UUID REFERENCES users(id) ON DELETE RESTRICT,
        channels JSON NOT NULL, event_preferences JSON NOT NULL, quiet_hours JSON NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX ix_notification_preferences_organization ON notification_preferences(organization_id);
    """)


def downgrade() -> None:
    _execute_statements("""
    DROP TABLE notification_preferences;
    DROP TABLE audit_logs;
    DROP TABLE device_events;
    DROP TABLE cleaning_events;
    DROP TABLE cleaning_tasks;
    DROP TABLE alert_events;
    DROP TABLE incidents;
    DROP TABLE score_inputs;
    DROP TABLE hygiene_scores;
    DROP TABLE sensor_readings;
    DROP TABLE telemetry_events;
    DROP TABLE sensors;
    DROP TABLE devices;
    DROP TABLE washrooms;
    DROP TABLE users;
    DROP TABLE facilities;
    DROP TABLE organizations;
    """)
