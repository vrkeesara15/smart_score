import pytest
from sqlalchemy import inspect

from app import database
from app.models import Base

EXPECTED_TABLES = {
    "users",
    "students",
    "exams",
    "questions",
    "rubrics",
    "submissions",
    "answers",
}


@pytest.mark.asyncio
async def test_tables_created():
    database.configure_engine("sqlite+aiosqlite:///:memory:")
    await database.init_db()

    assert database.engine is not None

    async with database.engine.begin() as conn:
        def get_tables(sync_conn):
            inspector = inspect(sync_conn)
            try:
                tables = set(inspector.get_table_names(schema="public"))
            except Exception:  # pragma: no cover - depends on backend features
                tables = set()
            if not tables:
                tables = set(inspector.get_table_names())
            return tables

        tables = await conn.run_sync(get_tables)

    missing = EXPECTED_TABLES - tables
    assert not missing, f"Missing tables: {missing}. Existing tables: {tables}"

    for table_name in EXPECTED_TABLES:
        assert table_name in Base.metadata.tables
