from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", include_in_schema=True)
def health(request: Request) -> dict[str, str]:
    """Process liveness. This deliberately does not imply database readiness."""
    return {
        "status": "ok",
        "checked_at": datetime.now(UTC).isoformat(),
        "request_id": request.state.request_id,
    }


@router.get("/ready", include_in_schema=True, response_model=None)
def ready(request: Request, db: Session = Depends(get_db)) -> dict[str, str] | JSONResponse:
    """Readiness check; returns no credentials or dependency internals."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": "Service not ready",
                "status": 503,
                "code": "database_unavailable",
                "detail": "A required service is unavailable.",
                "instance": request.url.path,
                "request_id": request.state.request_id,
            },
            headers={"X-Request-ID": request.state.request_id},
        )
    return {
        "status": "ok",
        "checked_at": datetime.now(UTC).isoformat(),
        "request_id": request.state.request_id,
    }
