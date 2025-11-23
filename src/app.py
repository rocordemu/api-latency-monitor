from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from poller import poll_endpoints
from storage import init_db, save_status
from dotenv import load_dotenv
import os
import uvicorn
import asyncio
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware

import logging
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

logger = logging.getLogger(__name__)
logging.basicConfig(filename='./logs/api-latency-monitor-app.log', encoding='utf-8', level=logging.INFO)

resource = Resource.create({"service.name": "api-latency-monitor"})

span_exporter = OTLPSpanExporter(
    endpoint="otel-collector.opentelemetry.svc.cluster.local:4317",  # Update with your OTEL Collector endpoint
    insecure=True  # Set to True if using an unencrypted connection
)

tracer_provider = TracerProvider(resource=resource)
span_processor = BatchSpanProcessor(span_exporter)
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)

# Create and set the logger provider
logger_provider = LoggerProvider()
set_logger_provider(logger_provider)

# Set up OTLP Log Exporter for logs
log_exporter = OTLPLogExporter(
    endpoint="otel-collector.opentelemetry.svc.cluster.local:4317",  # Update with your OTEL Collector endpoint
    insecure=True
)

# Set up log emitter provider and processor
log_processor = BatchLogRecordProcessor(log_exporter)
logger_provider.add_log_record_processor(log_processor)

# Set up logging to forward to OpenTelemetry Collector
otel_handler = LoggingHandler(logger_provider=logger_provider)
logging.getLogger().addHandler(otel_handler)

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI()
FastAPIInstrumentor.instrument_app(app)
# app.asgi_app = OpenTelemetryMiddleware(app.asgi_app)

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
        with tracer.start_as_current_span("poll-task") as parent_span:
            results = await poll_endpoints(ENDPOINTS, API_TOKEN)
            parent_span.add_event("Polled endpoints")
            logger.info("Polled endpoints: %s", results)
            for endpoint, result in results.items():
                with tracer.start_as_current_span("analyze-endpoint") as span:
                    span.add_event("Analyzing endpoint")
                    span.set_attribute("endpoint", endpoint)
                    span.set_attribute("status_code", result["status_code"])
                    status = "success" if result["status_code"] == 200 else "failure"
                    span.set_attribute("status", status)
                    span.set_attribute("latency", result["latency"])
                    requests_total.labels(endpoint=endpoint, status=status).inc()
                    latency_seconds.labels(endpoint=endpoint).observe(result["latency"])
                    uptime_percent.labels(endpoint=endpoint).set(100 if status == "success" else 0)
                    if "error" in result:
                        span.set_status(Status(StatusCode.ERROR, result["error"]))
                        span.record_exception(Exception(result["error"]))
                        logger.error("Error polling %s: %s", endpoint, result["error"])
                    if result["latency"] > 1.0 or result["status_code"] != 200:
                        logger.warning("Endpoint %s is unhealthy: Latency %s, Status %s", endpoint, result["latency"], result["status_code"])
                    else:
                        logger.info("Endpoint %s is healthy: Latency %s, Status %s", endpoint, result["latency"], result["status_code"])
                    save_status(endpoint, result["status_code"], result["latency"])
                    span.add_event("Saved status")
            parent_span.add_event("Sleeping until next poll")
            await asyncio.sleep(POLL_INTERVAL)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(poll_task())

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
