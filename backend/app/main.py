import logging
import time
from uuid import uuid4

from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router, users_router
from app.api.devices import router as devices_router
from app.api.health import router as health_router
from app.api.telemetry import legacy_router as telemetry_legacy_router, router as telemetry_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()
logger = logging.getLogger("iotsense.http")

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "IoTSense service foundation. Business endpoints will be added against "
        "the versioned contract in backend/openapi.yaml."
    ),
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
)
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(devices_router, prefix=settings.api_prefix)
app.include_router(telemetry_router)
app.include_router(telemetry_legacy_router)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-CSRF-Token", "X-Request-ID", "X-Device-Key"],
    )


@app.middleware("http")
async def request_context(request: Request, call_next):  # type: ignore[no-untyped-def]
    request_id = request.headers.get("x-request-id")
    if not request_id or len(request_id) > 100 or not request_id.isascii():
        request_id = str(uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "http_request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    logger.exception("unhandled_exception", extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": "Internal server error",
            "status": 500,
            "code": "internal_error",
            "detail": "The request could not be completed.",
            "instance": request.url.path,
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


@app.exception_handler(HTTPException)
async def http_problem(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    detail = exc.detail
    if isinstance(detail, dict):
        code = detail.get("code", "request_error")
        title = detail.get("title", "Request failed")
        message = detail.get("detail", "The request could not be completed.")
    else:
        code = "request_error"
        title = "Request failed"
        message = str(detail)
    return JSONResponse(
        status_code=exc.status_code,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": title,
            "status": exc.status_code,
            "code": code,
            "detail": message,
            "instance": request.url.path,
            "request_id": request_id,
        },
        headers={**(exc.headers or {}), "X-Request-ID": request_id},
    )


@app.exception_handler(RequestValidationError)
async def validation_problem(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    errors = [
        {"field": ".".join(str(part) for part in error.get("loc", ())), "message": "Invalid value."}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": "Request validation failed",
            "status": 422,
            "code": "validation_error",
            "detail": "One or more fields are invalid.",
            "instance": request.url.path,
            "request_id": request_id,
            "errors": errors,
        },
        headers={"X-Request-ID": request_id},
    )
