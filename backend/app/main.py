"""
Data & Security Copilot
FastAPI application entry point.
"""

from fastapi import FastAPI

from backend.app.api.alerts import router as alerts_router
from backend.app.api.auth import router as auth_router
from backend.app.api.users import router as users_router
from backend.app.api.audit import router as audit_router

# ============================================================
# Application
# ============================================================

app = FastAPI(
    title="Data & Security Copilot API",
    description=(
        "API for fraud detection, security alerts, " "and AI-assisted investigation."
    ),
    version="0.1.0",
)


# ============================================================
# Routers
# ============================================================

app.include_router(
    alerts_router,
)

app.include_router(
    auth_router,
)

app.include_router(
    users_router,
)

app.include_router(
    audit_router,
)

# ============================================================
# Health check
# ============================================================


@app.get(
    "/health",
    tags=["System"],
)
def health_check():
    """
    Basic application health check.
    """

    return {
        "status": "ok",
        "service": "data-security-copilot-api",
    }
