from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from quiz_router import router as quiz_router, logger
from database import engine, Base
import models

import uuid
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Application startup complete")

    yield


    logger.info("Application shutdown complete")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quiz_router)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        logger.info(
            f"Incoming request {request.method} {request.url.path}",
            extra={"correlation_id": correlation_id}
        )

        response = await call_next(request)

        process_time = round((time.time() - start_time) * 1000, 2)

        logger.info(
            f"Completed {request.method} {request.url.path} "
            f"status={response.status_code} "
            f"time_ms={process_time}",
            extra={"correlation_id": correlation_id}
        )

        response.headers["X-Correlation-ID"] = correlation_id
        return response

    except Exception:
        logger.exception(
            f"Unhandled error in {request.method} {request.url.path}",
            extra={"correlation_id": correlation_id}
        )
        raise