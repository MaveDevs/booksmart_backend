from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.api.v1.api import api_router
from app.core.monitoring import init_sentry

init_sentry()

def _is_jwt_auth_disabled() -> bool:
    return os.getenv("JWT_AUTH_DISABLED", "false").lower() == "true"


def _build_api_description() -> str:
    mode = "disabled (local testing)" if _is_jwt_auth_disabled() else "enabled"
    return (
        "Booksmart backend API.\n\n"
        f"Current auth mode: JWT {mode}.\n"
        "Set JWT_AUTH_DISABLED=true only for local testing."
    )


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
    allow_origins=["*"],  # In production, replace with specific origins
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


# Routers
app.include_router(api_router, prefix="/api/v1")