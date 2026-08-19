from fastapi import APIRouter

from backend.app.db.database import check_database_connection

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check() -> dict[str, object]:
    database_available = check_database_connection()

    return {
        "status": "ok" if database_available else "degraded",
        "database": "connected" if database_available else "unavailable",
    }
