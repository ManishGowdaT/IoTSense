from __future__ import annotations

import hashlib
import hmac
import secrets
import smtplib
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from threading import Lock
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pwdlib import PasswordHash
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models import AuditLog, Organization, PasswordResetToken, User, UserSession

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])
users_router = APIRouter(tags=["Administration"])
password_hasher = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hasher.hash("not-a-real-password-used-for-timing")
_login_attempts: dict[str, list[float]] = {}
_login_attempts_lock = Lock()

ROLE_VALUES = {"super_admin", "facility_admin", "maintenance_staff", "viewer"}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=32, max_length=256)
    new_password: str = Field(min_length=12, max_length=256)


class InviteUserRequest(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=120)
    role: str = Field(pattern="^(super_admin|facility_admin|maintenance_staff|viewer)$")
    organization_id: UUID | None = None

    @field_validator("display_name")
    @classmethod
    def display_name_not_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Display name cannot be blank.")
        return normalized


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    display_name: str
    role: str
    organization_id: UUID | None
    status: str


class UserPage(BaseModel):
    items: list[UserSummary]
    page: int
    page_size: int
    total: int
    has_more: bool


@dataclass(frozen=True)
class AuthContext:
    user: User
    session: UserSession


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalized_email(email: str) -> str:
    return email.strip().casefold()


def _problem(status_code: int, code: str, title: str, detail: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "title": title, "detail": detail},
    )


def _record_audit(
    db: Session,
    *,
    user: User,
    action: str,
    outcome: str = "success",
    resource_type: str = "user",
    resource_id: str | None = None,
) -> None:
    db.add(
        AuditLog(
            id=uuid4(),
            organization_id=user.organization_id,
            actor_user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id or str(user.id),
            outcome=outcome,
            metadata_json={},
        )
    )


def _set_session_cookies(response: Response, raw_session: str, csrf_token: str, ttl: int) -> None:
    response.set_cookie(
        settings.session_cookie_name,
        raw_session,
        max_age=ttl,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="strict",
        path="/",
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf_token,
        max_age=ttl,
        httponly=False,
        secure=settings.secure_cookies,
        samesite="strict",
        path="/",
    )


def _clear_session_cookies(response: Response) -> None:
    response.delete_cookie(settings.session_cookie_name, path="/", secure=settings.secure_cookies,
                           httponly=True, samesite="strict")
    response.delete_cookie(settings.csrf_cookie_name, path="/", secure=settings.secure_cookies,
                           httponly=False, samesite="strict")


def _new_session(db: Session, user: User) -> tuple[UserSession, str, str, int]:
    raw_token = secrets.token_urlsafe(48)
    csrf_token = secrets.token_urlsafe(32)
    ttl = settings.session_ttl_hours * 3600
    session_row = UserSession(
        id=uuid4(),
        user_id=user.id,
        token_hash=_digest(raw_token),
        csrf_token_hash=_digest(csrf_token),
        expires_at=datetime.now(UTC) + timedelta(seconds=ttl),
    )
    db.add(session_row)
    return session_row, raw_token, csrf_token, ttl


def _check_login_limit(request: Request, email: str) -> None:
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{email}"
    now = time.monotonic()
    window = settings.login_rate_limit_window_seconds
    with _login_attempts_lock:
        for expired_key in [
            current_key
            for current_key, attempts in _login_attempts.items()
            if not attempts or now - attempts[-1] >= window
        ]:
            _login_attempts.pop(expired_key, None)
        attempts = [stamp for stamp in _login_attempts.get(key, []) if now - stamp < window]
        if len(attempts) >= settings.login_rate_limit_attempts:
            raise _problem(429, "login_rate_limited", "Too many attempts", "Try again later.")
        attempts.append(now)
        _login_attempts[key] = attempts


def _clear_login_limit(request: Request, email: str) -> None:
    client_ip = request.client.host if request.client else "unknown"
    with _login_attempts_lock:
        _login_attempts.pop(f"{client_ip}:{email}", None)


def get_auth_context(
    request: Request,
    db: Session = Depends(get_db),
) -> AuthContext:
    raw_token = request.cookies.get(settings.session_cookie_name)
    if not raw_token:
        raise _problem(401, "authentication_required", "Authentication required", "Sign in to continue.")
    session_row = db.scalar(
        select(UserSession).where(
            UserSession.token_hash == _digest(raw_token),
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > datetime.now(UTC),
        )
    )
    if session_row is None:
        raise _problem(401, "session_expired", "Session expired", "Sign in again to continue.")
    user = db.get(User, session_row.user_id)
    if user is None or user.status != "active":
        raise _problem(401, "account_inactive", "Account unavailable", "Sign in again or contact an administrator.")
    return AuthContext(user=user, session=session_row)


def require_csrf(
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
    csrf_header: str | None = Header(default=None, alias="X-CSRF-Token"),
) -> AuthContext:
    csrf_cookie = request.cookies.get(settings.csrf_cookie_name)
    if (
        not csrf_header
        or not csrf_cookie
        or not hmac.compare_digest(csrf_header, csrf_cookie)
        or not hmac.compare_digest(_digest(csrf_header), auth.session.csrf_token_hash)
    ):
        raise _problem(403, "csrf_failed", "Request could not be verified", "Refresh the page and try again.")
    return auth


def require_roles(*roles: str):
    if any(role not in ROLE_VALUES for role in roles):
        raise ValueError("Unknown role in authorization policy")

    def dependency(auth: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if auth.user.role not in roles:
            raise _problem(403, "forbidden", "Forbidden", "You do not have permission to perform this action.")
        return auth

    return dependency


@router.post("/login", response_model=UserSummary)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)) -> UserSummary:
    email = _normalized_email(str(payload.email))
    _check_login_limit(request, email)
    user = db.scalar(select(User).where(User.email_normalized == email))
    password_hash = user.password_hash if user and user.password_hash else DUMMY_PASSWORD_HASH
    valid = password_hasher.verify(payload.password, password_hash)
    if not valid or user is None or user.status != "active":
        raise _problem(401, "invalid_credentials", "Sign-in failed", "Email or password is incorrect.")
    _clear_login_limit(request, email)
    _, raw_token, csrf_token, ttl = _new_session(db, user)
    user.last_login_at = datetime.now(UTC)
    _record_audit(db, user=user, action="auth.login")
    db.commit()
    _set_session_cookies(response, raw_token, csrf_token, ttl)
    return UserSummary(
        id=user.id,
        email=user.email_normalized,
        display_name=user.display_name,
        role=user.role,
        organization_id=user.organization_id,
        status=user.status,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> Response:
    auth.session.revoked_at = datetime.now(UTC)
    _record_audit(db, user=auth.user, action="auth.logout")
    db.commit()
    _clear_session_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UserSummary)
def current_user(auth: AuthContext = Depends(get_auth_context)) -> UserSummary:
    return UserSummary(
        id=auth.user.id,
        email=auth.user.email_normalized,
        display_name=auth.user.display_name,
        role=auth.user.role,
        organization_id=auth.user.organization_id,
        status=auth.user.status,
    )


@router.post("/refresh", response_model=UserSummary)
def refresh(
    response: Response,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> UserSummary:
    auth.session.revoked_at = datetime.now(UTC)
    _, raw_token, csrf_token, ttl = _new_session(db, auth.user)
    _record_audit(db, user=auth.user, action="auth.session_refresh")
    db.commit()
    _set_session_cookies(response, raw_token, csrf_token, ttl)
    return UserSummary(
        id=auth.user.id,
        email=auth.user.email_normalized,
        display_name=auth.user.display_name,
        role=auth.user.role,
        organization_id=auth.user.organization_id,
        status=auth.user.status,
    )


def _send_reset_email(email: str, raw_token: str, purpose: str = "password_reset") -> None:
    if not settings.smtp_host or not settings.smtp_from_email:
        return
    message = EmailMessage()
    message["Subject"] = "IoTSense account invitation" if purpose == "invitation" else "IoTSense password reset"
    message["From"] = settings.smtp_from_email
    message["To"] = email
    message.set_content(
        "Use this one-time token in the IoTSense password setup form. "
        f"It expires in {settings.password_reset_ttl_minutes} minutes.\n\n{raw_token}\n"
    )
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_starttls:
            smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password or "")
        smtp.send_message(message)


def _issue_reset_token(db: Session, user: User, purpose: str) -> tuple[PasswordResetToken, str]:
    raw_token = secrets.token_urlsafe(48)
    reset_row = PasswordResetToken(
        id=uuid4(),
        user_id=user.id,
        token_hash=_digest(raw_token),
        purpose=purpose,
        expires_at=datetime.now(UTC) + timedelta(minutes=settings.password_reset_ttl_minutes),
    )
    db.add(reset_row)
    return reset_row, raw_token


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(
    payload: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    _check_login_limit(request, "password-reset")
    email = _normalized_email(str(payload.email))
    user = db.scalar(select(User).where(User.email_normalized == email, User.status == "active"))
    if user and settings.smtp_host and settings.smtp_from_email:
        reset_row, raw_token = _issue_reset_token(db, user, "password_reset")
        db.commit()
        try:
            _send_reset_email(email, raw_token, "password_reset")
        except (OSError, smtplib.SMTPException):
            # Never expose account existence or the reset token in logs/responses.
            reset_row.used_at = datetime.now(UTC)
            db.commit()
    return {"message": "If the account is eligible, password reset instructions will be sent."}


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
def confirm_password_reset(payload: PasswordResetConfirm, response: Response, db: Session = Depends(get_db)) -> Response:
    reset_row = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == _digest(payload.token),
            PasswordResetToken.purpose.in_(("password_reset", "invitation")),
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > datetime.now(UTC),
        )
    )
    if reset_row is None:
        raise _problem(400, "invalid_reset_token", "Reset token invalid", "Request a new password reset.")
    user = db.get(User, reset_row.user_id)
    if user is None or (reset_row.purpose == "password_reset" and user.status != "active"):
        raise _problem(400, "invalid_reset_token", "Reset token invalid", "Request a new password reset.")
    if reset_row.purpose == "invitation" and user.status != "invited":
        raise _problem(400, "invalid_reset_token", "Reset token invalid", "Request a new password reset.")
    user.password_hash = password_hasher.hash(payload.new_password)
    if reset_row.purpose == "invitation":
        user.status = "active"
    reset_row.used_at = datetime.now(UTC)
    db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.revoked_at.is_(None),
    ).update({UserSession.revoked_at: datetime.now(UTC)}, synchronize_session=False)
    _record_audit(db, user=user, action="auth.password_reset")
    db.commit()
    _clear_session_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@users_router.get("/users", response_model=UserPage)
def list_users(
    page: int = 1,
    page_size: int = 50,
    auth: AuthContext = Depends(require_roles("super_admin", "facility_admin")),
    db: Session = Depends(get_db),
) -> UserPage:
    if page < 1 or page_size < 1 or page_size > 200:
        raise _problem(422, "invalid_pagination", "Invalid pagination", "Use page >= 1 and page_size from 1 to 200.")
    query = select(User)
    count_query = select(func.count()).select_from(User)
    if auth.user.role != "super_admin":
        query = query.where(User.organization_id == auth.user.organization_id)
        count_query = count_query.where(User.organization_id == auth.user.organization_id)
    total = db.scalar(count_query) or 0
    items = list(db.scalars(query.order_by(User.email_normalized).offset((page - 1) * page_size).limit(page_size)))
    return UserPage(
        items=[UserSummary(id=u.id, email=u.email_normalized, display_name=u.display_name,
                           role=u.role, organization_id=u.organization_id, status=u.status) for u in items],
        page=page,
        page_size=page_size,
        total=total,
        has_more=(page * page_size) < total,
    )


@users_router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserSummary)
def invite_user(
    payload: InviteUserRequest,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> UserSummary:
    if auth.user.role not in {"super_admin", "facility_admin"}:
        raise _problem(403, "forbidden", "Forbidden", "You do not have permission to invite users.")
    if not settings.smtp_host or not settings.smtp_from_email:
        raise _problem(503, "email_unavailable", "Invitation unavailable", "Configure email delivery before inviting users.")
    if auth.user.role == "facility_admin":
        if payload.organization_id not in (None, auth.user.organization_id):
            raise _problem(403, "forbidden", "Forbidden", "You can only invite users into your organization.")
        if payload.role not in {"maintenance_staff", "viewer"}:
            raise _problem(403, "forbidden", "Forbidden", "Facility Admins may invite Maintenance Staff or Viewers.")
        organization_id = auth.user.organization_id
    else:
        organization_id = payload.organization_id
        if payload.role != "super_admin" and organization_id is None:
            raise _problem(422, "organization_required", "Organization required", "Choose an organization for this user.")
        if payload.role == "super_admin" and organization_id is not None:
            raise _problem(422, "organization_not_allowed", "Organization not allowed", "Super Admin accounts are platform scoped.")
    if organization_id is not None and db.get(Organization, organization_id) is None:
        raise _problem(404, "organization_not_found", "Organization not found", "The organization does not exist.")
    email = _normalized_email(str(payload.email))
    if db.scalar(select(User.id).where(User.email_normalized == email)) is not None:
        raise _problem(409, "email_in_use", "Email already in use", "An account already uses this email.")
    user = User(
        id=uuid4(), organization_id=organization_id, email_normalized=email,
        display_name=payload.display_name.strip(), password_hash=None,
        role=payload.role, status="invited",
    )
    _, raw_token = _issue_reset_token(db, user, "invitation")
    db.add(user)
    _record_audit(db, user=auth.user, action="user.invite", resource_id=str(user.id))
    try:
        db.flush()
        _send_reset_email(email, raw_token, "invitation")
        db.commit()
    except (OSError, smtplib.SMTPException, IntegrityError) as exc:
        db.rollback()
        if isinstance(exc, IntegrityError):
            raise _problem(409, "email_in_use", "Email already in use", "An account already uses this email.") from exc
        raise _problem(503, "email_unavailable", "Invitation unavailable", "Email delivery failed. Try again later.") from exc
    return UserSummary(id=user.id, email=email, display_name=user.display_name,
                       role=user.role, organization_id=user.organization_id, status=user.status)


@users_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(
    user_id: UUID,
    response: Response,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> Response:
    if auth.user.role not in {"super_admin", "facility_admin"}:
        raise _problem(403, "forbidden", "Forbidden", "You do not have permission to deactivate users.")
    target = db.get(User, user_id)
    if target is None or (
        auth.user.role != "super_admin" and target.organization_id != auth.user.organization_id
    ):
        raise _problem(404, "user_not_found", "User not found", "The requested user does not exist.")
    if target.id == auth.user.id:
        raise _problem(409, "cannot_deactivate_self", "Action not allowed", "You cannot deactivate your own account.")
    if auth.user.role == "facility_admin" and target.role not in {"maintenance_staff", "viewer"}:
        raise _problem(403, "forbidden", "Forbidden", "Facility Admins may only deactivate Maintenance Staff or Viewers.")
    target.status = "inactive"
    now = datetime.now(UTC)
    db.query(UserSession).filter(
        UserSession.user_id == target.id, UserSession.revoked_at.is_(None)
    ).update({UserSession.revoked_at: now}, synchronize_session=False)
    _record_audit(db, user=auth.user, action="user.deactivate", resource_id=str(target.id))
    db.commit()
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
