import json
import logging
import random
import sys
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# Configuration
SERVICE_NAME = "payment-api"

# Possible values:
# None
# "database"
# "latency"
# "error_rate"
FAILURE_MODE = 'database'


# Structured JSON Logger

class JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:

        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "event": getattr(record, "event", "application_event"),
            "message": record.getMessage(),
        }

        # Add optional structured fields
        extra_fields = getattr(record, "extra_fields", {})

        if extra_fields:
            log_entry.update(extra_fields)

        return json.dumps(log_entry)


logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False


# FastAPI application

app = FastAPI(
    title="Simulated Payment API",
    description="Fake customer payment service for AI-SRE testing.",
    version="0.1.0",
)

# Request model
class PaymentRequest(BaseModel):
    user_id: str
    amount: float


# Request logging middleware

@app.middleware("http")
async def log_requests(request: Request, call_next):

    start_time = datetime.now(timezone.utc)

    try:

        response = await call_next(request)

        end_time = datetime.now(timezone.utc)

        duration = (
            end_time - start_time
        ).total_seconds()

        logger.info(
            "HTTP request completed",
            extra={
                "event": "http_request",
                "extra_fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_seconds": round(duration, 4),
                },
            },
        )

        return response

    except Exception:

        end_time = datetime.now(timezone.utc)

        duration = (
            end_time - start_time
        ).total_seconds()

        logger.exception(
            "Unhandled application exception",
            extra={
                "event": "unhandled_exception",
                "extra_fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "duration_seconds": round(duration, 4),
                },
            },
        )

        raise


# Health endpoint
@app.get("/health")
def health_check():

    if FAILURE_MODE == "database":

        logger.error(
            "Database connection failure detected",
            extra={
                "event": "database_connection_failure",
                "extra_fields": {
                    "failure_mode": FAILURE_MODE,
                },
            },
        )

        return {
            "status": "unhealthy",
            "service": SERVICE_NAME,
            "reason": "database connection failure",
        }

    logger.info(
        "Health check successful",
        extra={
            "event": "health_check",
            "extra_fields": {
                "status": "healthy",
            },
        },
    )

    return {
        "status": "healthy",
        "service": SERVICE_NAME,
    }


# Payment endpoint
@app.post("/payments")
def process_payment(payment: PaymentRequest):

    logger.info(
        "Payment request received",
        extra={
            "event": "payment_request",
            "extra_fields": {
                "user_id": payment.user_id,
                "amount": payment.amount,
                "failure_mode": FAILURE_MODE,
            },
        },
    )
    # Normal latency
    processing_time = random.uniform(0.05, 0.2)

    # Simulate high latency
    if FAILURE_MODE == "latency":

        processing_time = random.uniform(2, 5)

        logger.warning(
            "High latency failure mode active",
            extra={
                "event": "high_latency",
                "extra_fields": {
                    "user_id": payment.user_id,
                    "processing_time_seconds": round(
                        processing_time,
                        3,
                    ),
                },
            },
        )

    # Simulate processing time
    import time

    time.sleep(processing_time)

    # Simulate database failure

    if FAILURE_MODE == "database":

        logger.error(
            "Database connection pool exhausted",
            extra={
                "event": "database_error",
                "extra_fields": {
                    "user_id": payment.user_id,
                    "error_type": "connection_pool_exhausted",
                },
            },
        )

        raise HTTPException(
            status_code=500,
            detail="Database connection pool exhausted",
        )
    # Simulate high error rate

    if FAILURE_MODE == "error_rate":

        if random.random() < 0.5:

            logger.error(
                "Payment processing failed",
                extra={
                    "event": "payment_failure",
                    "extra_fields": {
                        "user_id": payment.user_id,
                        "amount": payment.amount,
                        "error_type": "payment_processing_failure",
                    },
                },
            )

            raise HTTPException(
                status_code=500,
                detail="Payment processing failed",
            )
        
    # Successful payment
    logger.info(
        "Payment processed successfully",
        extra={
            "event": "payment_success",
            "extra_fields": {
                "user_id": payment.user_id,
                "amount": payment.amount,
                "processing_time_seconds": round(
                    processing_time,
                    3,
                ),
            },
        },
    )

    return {
        "status": "success",
        "user_id": payment.user_id,
        "amount": payment.amount,
        "processing_time": round(
            processing_time,
            3,
        ),
    }