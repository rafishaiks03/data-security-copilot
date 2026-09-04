"""
Data & Security Copilot
FastAPI application entry point.
"""

from fastapi import FastAPI

from app.api.alerts import router as alerts_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.audit import router as audit_router
from app.api.data import router as data_router
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(
    data_router,
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
