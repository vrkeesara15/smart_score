import pytest
from sqlalchemy import inspect

from app.database import engine, init_db
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
    await init_db()

    async with engine.begin() as conn:
        def get_tables(sync_conn):
            inspector = inspect(sync_conn)
            return set(inspector.get_table_names(schema="public")) or set(inspector.get_table_names())

        tables = await conn.run_sync(get_tables)

    missing = EXPECTED_TABLES - tables
    assert not missing, f"Missing tables: {missing}. Existing tables: {tables}"

    for table_name in EXPECTED_TABLES:
        assert table_name in Base.metadata.tables
