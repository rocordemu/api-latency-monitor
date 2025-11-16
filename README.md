# API Latency Monitor

Monitors latency and availability of `/appRunning` endpoints for three IBM Cloud applications, with Prometheus metrics and Grafana dashboards.

## Architecture
![Architecture](docs/architecture.md)

## Setup
1. Clone the repo: `git clone https://github.com/rocordemu/api-latency-monitor.git`
2. (Optional) Create a virtual environment: `python -m venv src/.venv` and activate it (`source src/.venv/bin/activate` on Linux/Mac, `src\.venv\Scripts\activate` on Windows).
3. Install dependencies: `pip install -r src/requirements.txt`
4. Create `src/.env` from `src/.env.example` with your API token, URLs, and POLL_INTERVAL.
5. Run locally: `python src/app.py`

## Project Structure
```
.
├── Dockerfile
├── LICENSE
├── README.md
├── deploy
│   ├── alertmanager.yaml
│   ├── ansible_quickstart
│   │   └── inventory.ini
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── grafana.yaml
│   ├── infra.yaml
│   ├── prometheus
│   │   └── alert-rules.yaml
│   ├── prometheus.yaml
│   ├── secret.yaml
│   └── service.yaml
└── src
    ├── app.py
    ├── poller.py
    ├── requirements.txt
    ├── storage.py
    └── tests
        └── test_poller.py
```

## Deployment
1. Start Minikube: `minikube start --driver=docker`
2. Build Docker image: `docker build -t your-docker-repo/api-latency-monitor:latest .`
   - Note: `.dockerignore` excludes `src/.env`, `src/.venv`, and other temporary files.
3. Push image: `docker push your-docker-repo/api-latency-monitor:latest`
4. Create Secret: `kubectl create secret generic api-token --from-literal=token=$(grep API_TOKEN src/.env | cut -d '=' -f2 | tr -d ' \t\r\n') -n monitoring-project`
5. Apply manifests: `kubectl apply -f deploy/ -R`
6. Access service: `minikube service api-latency-monitor -n monitoring-project`

    ### Ansible
    - Run playbook: `ansible-playbook -i ansible_quickstart/inventory.ini ansible_quickstart/infra.yaml`

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