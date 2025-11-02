# API Latency Monitor

Monitors latency and availability of `/appRunning` endpoints for three IBM Cloud applications, with Prometheus metrics and Grafana dashboards.

## Architecture
![Architecture](docs/architecture.md)

## Setup
1. Clone the repo: `git clone <repo-url>`
2. (Optional) Create a virtual environment: `python -m venv src/.venv` and activate it (`source src/.venv/bin/activate` on Linux/Mac, `src\.venv\Scripts\activate` on Windows).
3. Install dependencies: `pip install -r src/requirements.txt`
4. Create `src/.env` from `src/.env.example` with your API token, URLs, and POLL_INTERVAL.
5. Run locally: `python src/app.py`

## Project Structure
```
api-latency-monitor/
├── main.py                # Main application script for polling APIs and exposing metrics
├── storage.py             # Module for storing latency data
├── requirements.txt       # Python dependencies
├── deploy/                # Kubernetes manifests and Helm chart configurations
│   ├── deployment.yaml    # Kubernetes Deployment for the application
│   ├── service.yaml       # Kubernetes Service for the application
│   ├── configmap.yaml     # Environment variables for API endpoints and poll interval
│   ├── secrets.yaml       # Kubernetes Secrets for API tokens
│   ├── prometheus.yaml    # Prometheus configuration (optional if using Helm)
│   └── grafana.yaml       # Grafana configuration (optional if using Helm)
├── charts/                # Helm charts for Prometheus and Grafana (if used)
├── Dockerfile             # Dockerfile for building the application image
└── README.md              # Project documentation
```

## Deployment
1. Start Minikube: `minikube start`
2. Build Docker image: `docker build -t your-docker-repo/api-latency-monitor:latest .`
   - Note: `.dockerignore` excludes `src/.env`, `src/.venv`, and other temporary files.
3. Push image: `docker push your-docker-repo/api-latency-monitor:latest`
4. Create Secret: `kubectl create secret generic api-token --from-literal=token=$(grep API_TOKEN src/.env | cut -d '=' -f2)`
5. Apply manifests: `kubectl apply -f deploy/`
6. Access service: `minikube service api-latency-monitor`

## Configuration
- **Local**: Environment variables are loaded from `src/.env` using `python-dotenv`.
- **Kubernetes**: Variables are injected from `deploy/configmap.yaml` (API_URL_1, API_URL_2, API_URL_3, POLL_INTERVAL) and `deploy/secret.yaml` (API_TOKEN).
- `POLL_INTERVAL`: Polling frequency in seconds (default: 60).
- Note: `src/.env` and `src/.venv` are not included in the Docker image (excluded by `.dockerignore`).

## Monitoring
- Prometheus: Scrapes `/metrics` endpoint.
- Grafana: Dashboards for latency, success/failure rates, and alerts.
- Alerts: Triggered for latency > 1s or HTTP errors (logged to console).

## Screenshots
- API response: `docs/screenshots/status.png`
- Grafana dashboard: `docs/screenshots/grafana.png`
- Kubernetes pods: `docs/screenshots/kubectl.png`

## Testing
Run tests: `pytest src/tests/test_poller.py`