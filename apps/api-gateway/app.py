import os
import time

import httpx
from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="API Gateway", version="1.0.0")

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8001")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8002")

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])
ACTIVE_REQUESTS = Gauge("http_requests_active", "Active HTTP requests")


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
    return {
        "service": "api-gateway",
        "version": "1.0.0",
        "endpoints": ["/health", "/metrics", "/orders", "/notifications"],
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/orders")
async def get_orders():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ORDER_SERVICE_URL}/orders")
        return response.json()


@app.post("/orders")
async def create_order(order: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{ORDER_SERVICE_URL}/orders", json=order)
        return response.json()


@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ORDER_SERVICE_URL}/orders/{order_id}")
        return response.json()


@app.get("/notifications")
async def get_notifications():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{NOTIFICATION_SERVICE_URL}/notifications")
        return response.json()


@app.post("/notifications")
async def create_notification(notification: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{NOTIFICATION_SERVICE_URL}/notifications", json=notification)
        return response.json()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
