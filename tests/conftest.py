import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from database import Base
from main import app
from quiz_router import get_db
from main import app

TEST_DATABASE_URL = "URL"


@pytest.fixture
async def async_session():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture(autouse=True)
async def override_get_db(async_session):
    async def _override():
        yield async_session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()