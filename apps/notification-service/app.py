import time
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Notification Service", version="1.0.0")

# In-memory store
notifications: list = []

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])
ACTIVE_REQUESTS = Gauge("http_requests_active", "Active HTTP requests")
NOTIFICATIONS_SENT = Counter("notifications_sent_total", "Total notifications sent", ["type"])


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    ACTIVE_REQUESTS.inc()
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(duration)
    ACTIVE_REQUESTS.dec()
    return response


@app.get("/")
async def root():
    return {"service": "notification-service", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "notification-service"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/notifications")
async def get_notifications():
    return {"notifications": notifications, "count": len(notifications)}


@app.post("/notifications")
async def create_notification(notification: dict):
    record = {
        "id": str(uuid.uuid4()),
        "type": notification.get("type", "info"),
        "message": notification.get("message", ""),
        "recipient": notification.get("recipient", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "sent",
    }
    notifications.append(record)
    NOTIFICATIONS_SENT.labels(record["type"]).inc()
    return record


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
