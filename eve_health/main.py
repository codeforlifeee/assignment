import os
import sys
from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend

from . import models, database
from .routers import users, centres, bookings, payments

# Configure Structured Logging
logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO", serialize=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    if os.environ.get("TESTING", "False").lower() != "true":
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        redis_cache = redis.from_url(redis_url, encoding="utf8")
        FastAPICache.init(RedisBackend(redis_cache), prefix="eve-cache")
    else:
        FastAPICache.init(InMemoryBackend(), prefix="eve-cache")
    yield
    logger.info("Application shutting down...")

app = FastAPI(
    title="EVE Healthcare Booking API",
    description="Backend service for diagnostic test bookings and simulated payments.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(users.router)
app.include_router(centres.router)
app.include_router(bookings.router)
app.include_router(payments.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to EVE Healthcare API. Visit /docs for Swagger documentation."}
