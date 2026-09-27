import os
import sys
from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger

from . import models, database
from .routers import users, centres, bookings, payments

# Configure Structured Logging
logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO", serialize=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    # Initialize rate limiter here if REDIS is available
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
