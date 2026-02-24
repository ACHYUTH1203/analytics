from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:impel300@localhost/ezwhelp"

engine = create_async_engine(DATABASE_URL, echo=True)
#IN PROD SET ECHO TO FALSE
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()