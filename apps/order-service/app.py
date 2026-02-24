import time
import uuid

from fastapi import FastAPI, Request, Response, HTTPException
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Order Service", version="1.0.0")

# In-memory store
orders: dict = {}

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])
ACTIVE_REQUESTS = Gauge("http_requests_active", "Active HTTP requests")
ORDERS_TOTAL = Counter("orders_created_total", "Total orders created")


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
    return {"service": "order-service", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "order-service"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/orders")
async def get_orders():
    return {"orders": list(orders.values()), "count": len(orders)}


@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders[order_id]


@app.post("/orders")
async def create_order(order: dict):
    order_id = str(uuid.uuid4())
    order_record = {
        "id": order_id,
        "status": "created",
        "items": order.get("items", []),
        "total": order.get("total", 0),
        "customer": order.get("customer", "unknown"),
    }
    orders[order_id] = order_record
    ORDERS_TOTAL.inc()
    return order_record


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
