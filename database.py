import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
#IN PROD SET ECHO TO FALSE
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()