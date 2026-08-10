from fastapi import FastAPI

from app.api.database import router as database_router
from app.api.health import router as health_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-powered database and security platform",
    version="0.1.0",
)


app.include_router(health_router)
app.include_router(database_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "application": settings.app_name,
        "version": "0.1.0",
        "message": "Data & Security Copilot API is running.",
    }
