from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(
    prefix="/api/v1/database",
    tags=["Database"],
)


@router.get("/info")
def database_info(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    result = db.execute(text("SELECT version()"))

    version = result.scalar_one()

    return {
        "database": "PostgreSQL",
        "version": version,
    }
