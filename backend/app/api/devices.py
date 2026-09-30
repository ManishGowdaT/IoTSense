from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.auth import AuthContext, require_csrf, require_roles
from app.db.session import get_db
from app.models import AuditLog, Device, Facility, Sensor, User, Washroom

router = APIRouter(prefix="/devices", tags=["Devices"])


def _problem(status_code: int, code: str, title: str, detail: str) -> HTTPException:
    return HTTPException(status_code, detail={"code": code, "title": title, "detail": detail})


def _organization_id(db: Session, washroom_id: UUID) -> UUID | None:
    return db.scalar(
        select(Facility.organization_id)
        .join(Washroom, Washroom.facility_id == Facility.id)
        .where(Washroom.id == washroom_id)
    )


def _can_access_device(db: Session, user: User, device: Device) -> bool:
    if user.role == "super_admin":
        return True
    return _organization_id(db, device.washroom_id) == user.organization_id


def _audit(db: Session, user: User, action: str, device: Device) -> None:
    db.add(AuditLog(
        id=uuid4(), organization_id=_organization_id(db, device.washroom_id),
        actor_user_id=user.id, action=action, resource_type="device",
        resource_id=str(device.id), outcome="success", metadata_json={},
    ))


class ProvisionDeviceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    washroom_id: UUID
    expected_sensor_keys: list[str] = Field(min_length=1, max_length=16)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank.")
        return value

    @field_validator("expected_sensor_keys")
    @classmethod
    def validate_sensor_keys(cls, values: list[str]) -> list[str]:
        allowed = {"bme680", "mq135", "mq3", "other"}
        if any(value not in allowed for value in values) or len(set(values)) != len(values):
            raise ValueError("Sensor keys must be unique supported values.")
        return values


class DeviceSummary(BaseModel):
    id: UUID
    name: str
    washroom_id: UUID
    status: str
    last_seen_at: datetime | None
    firmware_version: str | None
    sensor_keys: list[str]


class ProvisionedDevice(BaseModel):
    device: DeviceSummary
    device_key: str


class RotatedDeviceKey(BaseModel):
    device_id: UUID
    device_key: str


class DevicePage(BaseModel):
    items: list[DeviceSummary]
    page: int
    page_size: int
    total: int
    has_more: bool


def _summary(db: Session, device: Device) -> DeviceSummary:
    sensor_keys = list(db.scalars(
        select(Sensor.sensor_key).where(Sensor.device_id == device.id).order_by(Sensor.sensor_key)
    ))
    return DeviceSummary(
        id=device.id, name=device.name, washroom_id=device.washroom_id,
        status="revoked" if device.revoked_at is not None else device.status,
        last_seen_at=device.last_seen_at, firmware_version=device.firmware_version,
        sensor_keys=sensor_keys,
    )


@router.get("", response_model=DevicePage)
def list_devices(
    page: int = 1,
    page_size: int = 50,
    auth: AuthContext = Depends(require_roles("super_admin", "facility_admin", "maintenance_staff", "viewer")),
    db: Session = Depends(get_db),
) -> DevicePage:
    if page < 1 or page_size < 1 or page_size > 200:
        raise _problem(422, "invalid_pagination", "Invalid pagination", "Use page >= 1 and page_size from 1 to 200.")
    query = select(Device)
    count_query = select(func.count()).select_from(Device)
    if auth.user.role != "super_admin":
        scoped = select(Washroom.id).join(Facility, Facility.id == Washroom.facility_id).where(
            Facility.organization_id == auth.user.organization_id
        )
        query = query.where(Device.washroom_id.in_(scoped))
        count_query = count_query.where(Device.washroom_id.in_(scoped))
    total = db.scalar(count_query) or 0
    rows = list(db.scalars(query.order_by(Device.name, Device.id).offset((page - 1) * page_size).limit(page_size)))
    return DevicePage(items=[_summary(db, row) for row in rows], page=page, page_size=page_size,
                      total=total, has_more=page * page_size < total)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProvisionedDevice)
def provision_device(
    payload: ProvisionDeviceRequest,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> ProvisionedDevice:
    if auth.user.role not in {"super_admin", "facility_admin"}:
        raise _problem(403, "forbidden", "Forbidden", "Only administrators may provision devices.")
    organization_id = _organization_id(db, payload.washroom_id)
    if organization_id is None:
        raise _problem(404, "washroom_not_found", "Washroom not found", "The requested washroom does not exist.")
    if auth.user.role == "facility_admin" and organization_id != auth.user.organization_id:
        raise _problem(404, "washroom_not_found", "Washroom not found", "The requested washroom does not exist.")

    raw_key = secrets.token_urlsafe(48)
    device = Device(
        id=uuid4(), washroom_id=payload.washroom_id, name=payload.name,
        device_key_hash=hashlib.sha256(raw_key.encode()).hexdigest(), status="unknown",
    )
    db.add(device)
    db.flush()
    for key in payload.expected_sensor_keys:
        db.add(Sensor(id=uuid4(), device_id=device.id, sensor_key=key,
                      model="unverified", sensor_type="unverified", status="unverified",
                      interface_metadata={}, calibration_metadata={}))
    db.add(AuditLog(
        id=uuid4(), organization_id=organization_id, actor_user_id=auth.user.id,
        action="device.provision", resource_type="device", resource_id=str(device.id),
        outcome="success", metadata_json={"sensor_keys": payload.expected_sensor_keys},
    ))
    db.commit()
    db.refresh(device)
    return ProvisionedDevice(device=_summary(db, device), device_key=raw_key)


@router.get("/{device_id}", response_model=DeviceSummary)
def get_device(
    device_id: UUID,
    auth: AuthContext = Depends(require_roles("super_admin", "facility_admin", "maintenance_staff", "viewer")),
    db: Session = Depends(get_db),
) -> DeviceSummary:
    device = db.get(Device, device_id)
    if device is None or not _can_access_device(db, auth.user, device):
        raise _problem(404, "device_not_found", "Device not found", "The requested device does not exist.")
    return _summary(db, device)


@router.post("/{device_id}/revoke", status_code=status.HTTP_204_NO_CONTENT)
def revoke_device(
    device_id: UUID,
    response: Response,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> Response:
    if auth.user.role not in {"super_admin", "facility_admin"}:
        raise _problem(403, "forbidden", "Forbidden", "Only administrators may revoke device credentials.")
    device = db.get(Device, device_id)
    if device is None or not _can_access_device(db, auth.user, device):
        raise _problem(404, "device_not_found", "Device not found", "The requested device does not exist.")
    if device.revoked_at is None:
        device.revoked_at = datetime.now(UTC)
        device.status = "revoked"
        _audit(db, auth.user, "device.revoke", device)
        db.commit()
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/{device_id}/rotate-key", response_model=RotatedDeviceKey)
def rotate_device_key(
    device_id: UUID,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> RotatedDeviceKey:
    if auth.user.role not in {"super_admin", "facility_admin"}:
        raise _problem(403, "forbidden", "Forbidden", "Only administrators may rotate device credentials.")
    device = db.get(Device, device_id)
    if device is None or not _can_access_device(db, auth.user, device):
        raise _problem(404, "device_not_found", "Device not found", "The requested device does not exist.")
    if device.revoked_at is not None:
        raise _problem(409, "device_revoked", "Device revoked", "A revoked device cannot receive a new credential.")
    raw_key = secrets.token_urlsafe(48)
    device.device_key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    device.key_rotated_at = datetime.now(UTC)
    _audit(db, auth.user, "device.rotate_key", device)
    db.commit()
    return RotatedDeviceKey(device_id=device.id, device_key=raw_key)
