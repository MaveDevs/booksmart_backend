from dotenv import load_dotenv
load_dotenv()
import asyncio
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.api.v1.api import api_router
from app.core.monitoring import init_sentry
from app.tasks.notification_worker import run_notification_worker

init_sentry()
logger = logging.getLogger(__name__)

def _is_jwt_auth_disabled() -> bool:
    return os.getenv("JWT_AUTH_DISABLED", "false").lower() == "true"


def _build_api_description() -> str:
    mode = "disabled (local testing)" if _is_jwt_auth_disabled() else "enabled"
    return (
        "Booksmart backend API.\n\n"
        f"Current auth mode: JWT {mode}.\n"
        "Set JWT_AUTH_DISABLED=true only for local testing."
    )


def _is_notification_worker_enabled() -> bool:
    return os.getenv("NOTIFICATION_WORKER_ENABLED", "false").lower() == "true"


app = FastAPI(
    title="Booksmart Backend API",
    version="1.0.0",
    description=_build_api_description(),
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    if _is_jwt_auth_disabled():
        for path_item in openapi_schema.get("paths", {}).values():
            for operation in path_item.values():
                if isinstance(operation, dict):
                    operation.pop("security", None)

        components = openapi_schema.get("components", {})
        security_schemes = components.get("securitySchemes")
        if isinstance(security_schemes, dict):
            security_schemes.pop("HTTPBearer", None)
            if not security_schemes:
                components.pop("securitySchemes", None)

        openapi_schema["x-auth-mode"] = "jwt-disabled-local"

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://192.168.0.152:4200",
        "http://localhost:8100", # Ionic/Capacitor potentially
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Admin:
# from app.db.session import engine
# admin = Admin(app, engine)
# admin.add_view(UserAdmin)

@app.get("/")
def root():
    return {"message": "Welcome to backend", "status": "active"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_notification_worker() -> None:
    if not _is_notification_worker_enabled():
        return

    poll_seconds = int(os.getenv("NOTIFICATION_WORKER_POLL_SECONDS", "60"))
    batch_size = int(os.getenv("NOTIFICATION_WORKER_BATCH_SIZE", "200"))

    app.state.notification_worker_stop_event = asyncio.Event()
    app.state.notification_worker_task = asyncio.create_task(
        run_notification_worker(
            poll_seconds=poll_seconds,
            batch_size=batch_size,
            stop_event=app.state.notification_worker_stop_event,
        )
    )
    logger.info("Notification worker enabled and started")


@app.on_event("shutdown")
async def shutdown_notification_worker() -> None:
    task = getattr(app.state, "notification_worker_task", None)
    stop_event = getattr(app.state, "notification_worker_stop_event", None)

    if not task:
        return

    if stop_event:
        stop_event.set()

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    logger.info("Notification worker stopped")


# Routers
app.include_router(api_router, prefix="/api/v1")