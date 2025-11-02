from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from poller import poll_endpoints
from storage import init_db, save_status
from dotenv import load_dotenv
import os
import uvicorn
import asyncio

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI()

# Prometheus metrics
requests_total = Counter("api_requests_total", "Total API requests", ["endpoint", "status"])
latency_seconds = Histogram("api_latency_seconds", "API response latency", ["endpoint"])
uptime_percent = Gauge("api_uptime_percent", "API uptime percentage", ["endpoint"])

# Prometheus ASGI middleware
prometheus_app = make_asgi_app()
app.mount("/metrics", prometheus_app)

# API endpoints to monitor
ENDPOINTS = [
    os.getenv("API_URL_1"),
    os.getenv("API_URL_2"),
    os.getenv("API_URL_3")
]
API_TOKEN = os.getenv("API_TOKEN")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "60"))  # Default to 60 seconds

# Initialize database
init_db()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/status")
async def get_status():
    # Fetch latest status from SQLite
    from storage import get_latest_status
    return get_latest_status()

async def poll_task():
    while True:
        results = await poll_endpoints(ENDPOINTS, API_TOKEN)
        for endpoint, result in results.items():
            status = "success" if result["status_code"] == 200 else "failure"
            requests_total.labels(endpoint=endpoint, status=status).inc()
            latency_seconds.labels(endpoint=endpoint).observe(result["latency"])
            uptime_percent.labels(endpoint=endpoint).set(100 if status == "success" else 0)
            if result["latency"] > 1.0 or result["status_code"] >= 500:
                print(f"Alert: {endpoint} - Latency: {result['latency']}s, Status: {result['status_code']}")
            save_status(endpoint, result["status_code"], result["latency"])
        await asyncio.sleep(POLL_INTERVAL)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(poll_task())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)