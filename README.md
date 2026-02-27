# EZWHELP Analytics Engine

Rule-based quiz engine and analytics backend built with:

- FastAPI
- PostgreSQL
- SQLAlchemy (Async)
- Alembic
- Pytest
- Poetry

## Features

- Deterministic rule engine (structural + lifecycle)
- Versioned engine logic
- Async persistence layer
- Structured JSON logging
- 34 test cases
- Alembic migrations

## Setup

### 1. Install dependencies
poetry install

### 2. Create .env file
DATABASE_URL=postgresql+asyncpg://user:password@localhost/quizdb

### 3. Run migrations
alembic upgrade head

### 4. Start server
poetry run uvicorn main:app --reload

### 5. Run tests
poetry run pytest -v