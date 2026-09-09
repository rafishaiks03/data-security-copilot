"""
Data Explorer API endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import require_roles
from app.db.database import get_database_connection

router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data Explorer"],
)


ALLOWED_ROLES = (
    "SECURITY_ADMIN",
    "SECURITY_ANALYST",
    "AUDITOR",
)


def get_public_tables(connection) -> list[str]:
    query = """
        SELECT
            table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    return [row[0] for row in rows]


def get_table_columns(
    connection,
    table_name: str,
) -> list[dict[str, str]]:
    query = """
        SELECT
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
        ORDER BY ordinal_position
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (table_name,))
        rows = cursor.fetchall()

    return [
        {
            "name": row[0],
            "type": row[1],
        }
        for row in rows
    ]


@router.get("/tables")
def list_tables(
    current_user: dict = Depends(require_roles(*ALLOWED_ROLES)),
):
    """
    Return user-accessible tables from the public schema.
    """

    try:
        with get_database_connection() as connection:
            tables = get_public_tables(connection)

        return {
            "count": len(tables),
            "tables": tables,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve database tables.",
        ) from exc


@router.get("/tables/{table_name}")
def get_table_data(
    table_name: str,
    limit: int = Query(
        default=25,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    search: str | None = Query(
        default=None,
        max_length=200,
    ),
    filter_column: str | None = Query(
        default=None,
        max_length=100,
    ),
    filter_value: str | None = Query(
        default=None,
        max_length=200,
    ),
    filter_mode: str = Query(
        default="contains",
        pattern="^(contains|equals)$",
    ),
    sort_by: str | None = Query(
        default=None,
        max_length=100,
    ),
    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
    ),
    current_user: dict = Depends(require_roles(*ALLOWED_ROLES)),
):
    """
    Return filtered, sorted and paginated data
    for a public database table.
    """

    try:
        with get_database_connection() as connection:
            # -------------------------------------------------
            # 1. Validate table
            # -------------------------------------------------

            tables = get_public_tables(connection)

            if table_name not in tables:
                raise HTTPException(
                    status_code=404,
                    detail=f"Table '{table_name}' not found.",
                )

            # -------------------------------------------------
            # 2. Get column metadata
            # -------------------------------------------------

            columns = get_table_columns(
                connection,
                table_name,
            )

            column_names = [column["name"] for column in columns]

            if not column_names:
                raise HTTPException(
                    status_code=404,
                    detail=f"Table '{table_name}' has no columns.",
                )

            # -------------------------------------------------
            # 3. Validate filter column
            # -------------------------------------------------

            if filter_column and filter_column not in column_names:
                raise HTTPException(
                    status_code=400,
                    detail=(f"Invalid filter column " f"'{filter_column}'."),
                )

            if filter_value is not None and not filter_column:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "filter_column is required when " "filter_value is provided."
                    ),
                )

            # -------------------------------------------------
            # 4. Validate sort column
            # -------------------------------------------------

            if sort_by and sort_by not in column_names:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid sort column '{sort_by}'.",
                )

            sort_column = sort_by or column_names[0]

            # -------------------------------------------------
            # 5. Build WHERE clauses
            # -------------------------------------------------

            where_clauses: list[str] = []
            query_params: list[object] = []

            if search:
                search_pattern = f"%{search}%"

                search_clauses = [
                    f'CAST("{column}" AS TEXT) ILIKE %s' for column in column_names
                ]

                where_clauses.append("(" + " OR ".join(search_clauses) + ")")

                query_params.extend([search_pattern] * len(column_names))

            if filter_column and filter_value is not None:
                quoted_filter_column = f'"{filter_column}"'

                if filter_mode == "equals":
                    where_clauses.append(f"CAST({quoted_filter_column} AS TEXT) = %s")
                    query_params.append(filter_value)
                else:
                    where_clauses.append(
                        f"CAST({quoted_filter_column} AS TEXT) ILIKE %s"
                    )
                    query_params.append(f"%{filter_value}%")

            where_sql = ""

            if where_clauses:
                where_sql = "WHERE " + " AND ".join(where_clauses)

            # -------------------------------------------------
            # 6. Count filtered rows
            # -------------------------------------------------

            count_query = f"""
                SELECT COUNT(*)
                FROM "public"."{table_name}"
                {where_sql}
            """

            with connection.cursor() as cursor:
                cursor.execute(
                    count_query,
                    query_params,
                )
                total_count = cursor.fetchone()[0]

            # -------------------------------------------------
            # 7. Fetch filtered/sorted/paginated rows
            # -------------------------------------------------

            direction = "DESC" if sort_order == "desc" else "ASC"

            data_query = f"""
                SELECT *
                FROM "public"."{table_name}"
                {where_sql}
                ORDER BY "{sort_column}" {direction}
                LIMIT %s
                OFFSET %s
            """

            data_params = [
                *query_params,
                limit,
                offset,
            ]

            with connection.cursor() as cursor:
                cursor.execute(
                    data_query,
                    data_params,
                )

                rows = cursor.fetchall()

                result_column_names = [
                    description[0] for description in cursor.description
                ]

            data = [dict(zip(result_column_names, row)) for row in rows]

        return {
            "table": table_name,
            "columns": columns,
            "count": total_count,
            "limit": limit,
            "offset": offset,
            "search": search,
            "filter_column": filter_column,
            "filter_value": filter_value,
            "filter_mode": filter_mode,
            "sort_by": sort_column,
            "sort_order": sort_order,
            "rows": data,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve table data.",
        ) from exc
