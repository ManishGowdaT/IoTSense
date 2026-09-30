"""Create an initial organization through an explicit local operator action."""

from uuid import uuid4

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Organization


def main() -> None:
    name = input("Organization name: ").strip()
    if not name:
        raise SystemExit("Organization name is required.")
    with SessionLocal() as db:
        if db.scalar(select(Organization.id).where(Organization.name == name)):
            raise SystemExit("An organization with that name already exists.")
        organization = Organization(id=uuid4(), name=name, status="active")
        db.add(organization)
        db.commit()
        print(f"Created organization {organization.name} with ID {organization.id}")


if __name__ == "__main__":
    main()
