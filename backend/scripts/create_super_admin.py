"""Interactively create the first platform administrator."""

from getpass import getpass
from uuid import uuid4

from email_validator import EmailNotValidError, validate_email
from pwdlib import PasswordHash
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import AuditLog, User


def main() -> None:
    raw_email = input("Super Admin email: ").strip()
    display_name = input("Display name: ").strip()
    password = getpass("Password (minimum 12 characters): ")
    confirmation = getpass("Confirm password: ")
    if len(password) < 12 or password != confirmation:
        raise SystemExit("Password must be at least 12 characters and both entries must match.")
    if not display_name:
        raise SystemExit("Display name is required.")
    try:
        email = validate_email(raw_email, check_deliverability=False).normalized.casefold()
    except EmailNotValidError as exc:
        raise SystemExit("Enter a valid email address.") from exc
    hasher = PasswordHash.recommended()
    with SessionLocal() as db:
        if db.scalar(select(User.id).where(User.email_normalized == email)):
            raise SystemExit("An account already exists with that email.")
        user = User(
            id=uuid4(),
            organization_id=None,
            email_normalized=email,
            display_name=display_name,
            password_hash=hasher.hash(password),
            role="super_admin",
            status="active",
        )
        db.add(user)
        db.flush()
        db.add(
            AuditLog(
                id=uuid4(),
                organization_id=None,
                actor_user_id=user.id,
                action="auth.bootstrap_super_admin",
                resource_type="user",
                resource_id=str(user.id),
                outcome="success",
                metadata_json={},
            )
        )
        db.commit()
    print(f"Created Super Admin account: {email}")


if __name__ == "__main__":
    main()
