# API Latency Monitor

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI Status](https://github.com/rocordemu/api-latency-monitor/actions/workflows/main.yml/badge.svg)](https://github.com/rocordemu/api-latency-monitor/actions)
[![CI Status](https://github.com/rocordemu/api-latency-monitor/actions/workflows/python-app.yml/badge.svg)](https://github.com/rocordemu/api-latency-monitor/actions)
[![Docker Pulls](https://img.shields.io/docker/pulls/rocordemu/api-latency-monitor)](https://hub.docker.com/r/rocordemu/api-latency-monitor)

A Python-based application for monitoring the latency and availability of `/appRunning` endpoints for three IBM Cloud applications. It polls the endpoints, records metrics, stores data in SQLite, exposes Prometheus metrics, and integrates with Grafana for visualization and alerting. The project is containerized with Docker and deployed on Kubernetes, with CI/CD workflows and optional Ansible automation for infrastructure setup.

This project demonstrates SRE principles, including observability, alerting, tracing, and secure configuration management.

## Features

This application provides a comprehensive monitoring solution with the following key features, explained in detail:

1. **API Polling and Latency Measurement:**
   - The core functionality is handled by `poller.py`, which asynchronously polls the `/appRunning` endpoints of three IBM Cloud applications at a configurable interval (default: 60 seconds).
   - Measures response latency using `time.time()` and handles errors (e.g., timeouts, non-200 status codes) gracefully.
   - Records status codes and latency for each endpoint, classifying responses as "success" (200 OK) or "failure" (any other code).
   - Feature benefit: Enables real-time detection of API performance issues, such as high latency or downtime.

2. **Prometheus Metrics Exposure:**
   - Uses `prometheus_client` to expose custom metrics: 
     - `api_requests_total` (Counter): Total requests per endpoint, labeled by status ("success" or "failure").
     - `api_latency_seconds` (Histogram): Response latency per endpoint, with buckets for percentile calculations (e.g., P95).
     - `api_uptime_percent` (Gauge): Uptime percentage per endpoint (100 for success, 0 for failure).
   - Metrics are served via a FastAPI-mounted endpoint at `/metrics`.
   - Feature benefit: Allows seamless integration with Prometheus for time-series data collection, enabling alerting and visualization.

3. **SQLite Data Persistence:**
   - `storage.py` initializes a SQLite database (`status.db`) and saves polling results (endpoint, status code, latency, timestamp).
   - Supports querying latest status via `/status` endpoint.
   - Uses `os.makedirs` for directory creation and handles path differences for local vs. Kubernetes environments.
   - Feature benefit: Provides persistent storage for historical analysis, surviving pod restarts (via `emptyDir` or PVC).

4. **FastAPI Web Server:**
   - `app.py` runs a FastAPI server on port 8000, with endpoints:
     - `/health`: Returns {"status": "healthy"} for liveness probes.
     - `/status`: Returns latest status from SQLite.
     - `/metrics`: Prometheus metrics (mounted using `make_asgi_app`).
   - Background polling task using asyncio.
   - Feature benefit: Exposes a REST API for manual checks and integrates with Kubernetes probes for health management.

5. **Kubernetes Deployment:**
   - Manifests in `deploy/` for Deployment, Service, ConfigMap, Secret, and PersistentVolume.
   - Supports namespace `monitoring-project`.
   - Uses `hostNetwork` for cAdvisor DaemonSet to monitor container metrics.
   - Feature benefit: Enables scalable, resilient deployment with auto-restarts and resource limits.

6. **Monitoring Stack (Prometheus, Grafana, cAdvisor, Jaeger, Loki):**
   - Prometheus scrapes metrics and defines alert rules (e.g., high latency >1s, error rate >5%).
   - Grafana for dashboards (latency P95, request rate, error rate) and alerts via Slack.
   - cAdvisor DaemonSet for container CPU/memory metrics.
   - Jaeger for tracing.
   - Loki for logs.
   - Feature benefit: Full observability with metrics, logs, traces, and alerts for proactive SRE.

7. **Alerting with Slack Integration:**
   - Alert rules in Prometheus trigger on high latency, error rate, or uptime <90%.
   - Grafana sends notifications to Slack via webhook.
   - Feature benefit: Immediate alerts for incidents, enabling fast response.

8. **CI/CD Workflows:**
   - GitHub Actions: `ci` builds and pushes Docker image on `src/**` changes.
   - `Python Application` workflow runs tests and lint on pull requests.
   - Feature benefit: Automates building, testing, and deployment for reliability.

9. **Ansible Automation:**
   - `infra.yaml` playbook applies Kubernetes manifests and creates secrets.
   - Inventory in `inventory.ini` targets local Minikube.
   - Feature benefit: One-command setup for infrastructure, ideal for reproducible environments.

10. **Testing:**
    - `test_poller.py` for unit tests using pytest.
    - Feature benefit: Ensures polling logic is reliable.

11. **Security & Configuration:**
    - Secrets for API token and Slack webhook (created via `kubectl`, not committed).
    - `.dockerignore` excludes sensitive files.
    - Environment variables from `.env` for local dev.
    - Feature benefit: Secure handling of credentials, no hardcoding.

## Prerequisites

- Python 3.8+ for local development.
- Docker for building the image.
- Minikube or a Kubernetes cluster for deployment.
- GitHub account for CI/CD (optional).
- IBM Cloud API token and endpoint URLs.
- Slack webhook for alerts (optional).

## Setup
1. Clone the repo:
   ```bash
   git clone https://github.com/rocordemu/api-latency-monitor.git
   cd api-latency-monitor
   ```
2. (Optional) Create a virtual environment:
    ```bash
    python -m venv src/.venv
    source src/.venv/bin/activate  # Linux/Mac
    # or src\.venv\Scripts\activate on Windows
    ```
3. Install dependencies:
    ```bash
    pip install -r src/requirements.txt
    ```
4. Create `src/.env` based on 
    ```bash
    API_URL_1=https://app1.example.com/appRunning
    API_URL_2=https://app2.example.com/appRunning
    API_URL_3=https://app3.example.com/appRunning
    API_TOKEN=your-ibm-token
    POLL_INTERVAL=60
    SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook
    ```
5. Run locally:
    ```bash
    python src/app.py
    ```
6. Access endpoints:
- `http://localhost:8000/health`: Health check.
- `http://localhost:8000/status`: Latest API status.
- `http://localhost:8000/metrics`: Prometheus metrics.


## Project Structure
The repository is structured for easy navigation, with source code, deployment manifests, and automation scripts separated:
```
.
├── CONTRIBUTING.md
├── Dockerfile
├── LICENSE
├── README.md
├── ansible_quickstart
│   ├── infra.yaml
│   └── inventory.ini
├── deploy
│   ├── alertmanager.yaml
│   ├── cadvisor.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── grafana-loki.yaml
│   ├── grafana.yaml
│   ├── jaeger.yaml
│   ├── otel-collector.yaml
│   ├── prometheus
│   │   └── alert-rules.yaml
│   ├── prometheus-rbac-cluster.yaml
│   ├── prometheus.yaml
│   ├── secret.yaml
│   └── service.yaml
│   └── storage.yaml
└── src
    ├── app.py
    ├── poller.py
    ├── requirements.txt
    ├── storage.py
    └── tests
        └── test_poller.py
```

## Deployment
### Docker Containerization
1. Build the image:
    ```bash
    docker build -t your-docker-repo/api-latency-monitor:latest .
    ```
2. Push to your registry:
    ```bash
    docker push your-docker-repo/api-latency-monitor:latest
    ```

### Kubernetes Deployment
1. Start Minikube (if local):
    ```bash
    minikube start --driver=docker
    ```
2. Create secrets (securely, without committing):
    ```bash
    kubectl create secret generic api-token --from-literal=token=$(grep API_TOKEN src/.env | cut -d '=' -f2 | tr -d ' \t\r\n') -n monitoring-project
    kubectl create secret generic slack-webhook --from-literal=token=$(grep SLACK_WEBHOOK_URL src/.env | cut -d '=' -f2 | tr -d ' \t\r\n') -n monitoring-project
    ```
3. Apply all manifests recursively:
    ```bash
    kubectl apply -f deploy/ -R
    ```
4. Verify components:
- Deployments: `kubectl get deployments -n monitoring-project`
- Pods: `kubectl get pods -n monitoring-project`
- Services: `kubectl get services -n monitoring-project`
- ConfigMaps: `kubectl get configmaps -n monitoring-project`
- Secrets: `kubectl get secrets -n monitoring-project`
5. Access the app:
    ```bash
    minikube service api-latency-monitor -n monitoring-project
    ```

### Ansible Automation
For one-command deployment:
1. Install Ansible (if not installed):
    ```bash
    pip install ansible
    ```
2. Run playbook:
    ```bash
    ansible-playbook -i ansible_quickstart/inventory.ini ansible_quickstart/infra.yaml
    ```
The playbook applies all Kubernetes manifests and creates secrets from `.env`, ensuring reproducible setup.

## Configuration
- **Local Development:** Environment variables are loaded from `src/.env` using `dotenv`. This includes `API_URL_1/2/3` (endpoint URLs), `API_TOKEN` (IBM Cloud token), `POLL_INTERVAL` (polling frequency in seconds), and `SLACK_WEBHOOK_URL` (for alerts).
- **Kubernetes:** Variables are injected via `ConfigMap` (`deploy/configmap.yaml`) for non-sensitive data (URLs, interval) and `Secret` (`deploy/secret.yaml`) for sensitive data (token, webhook). The app uses `os.getenv` to load them.
- **Customization:** Adjust `POLL_INTERVAL` for faster/slower polling. Secrets are created dynamically to avoid committing sensitive info.
- **Security Note:** `.dockerignore` excludes `.env` and `.venv` from the image, ensuring no sensitive data is baked in.

## Kubernetes Integration
The project is fully Kubernetes-native:
- **Namespace:** All components are deployed in `monitoring-project`.
- **Deployment:** The app runs as a Deployment with replicas=1, liveness probes on `/health`, and resource limits (CPU/memory) for stability.
- **Service:** ClusterIP type exposing port 8000 for internal access.
- **Storage:** PersistentVolumeClaim for SQLite and Loki data persistence.
- **Monitoring Add-ons:** Includes cAdvisor for container metrics, Loki for logs, Jaeger for traces, and OpenTelemetry Collector for unified observability.
- **Screenshots:**
    - Deployments
    ![Deployments](./screenshots/Kubernetes%20Deployments.png)
    - Pods
    ![Pods](./screenshots/Kubernetes%20Pods.png)
    - Services
    ![Services](./screenshots/Kubernetes%20Services.png)
    - Config Maps
    ![ConfigMaps](./screenshots/Kubernetes%20Config%20Maps.png)
    - Secrets
    ![Secrets](./screenshots/Kubernetes%20Secrets.png)
    - Persistent Volumens
    ![PVC](./screenshots/Kubernetes%20PVC.png)

## Application Metrics
The app exposes custom Prometheus metrics at `/metrics`:
- **`api_requests_total{endpoint, status}`:** Counts requests per endpoint and status (success/failure).
- **`api_latency_seconds{endpoint}`:** Histogram of latency per endpoint (buckets for percentiles).
- **`api_uptime_percent{endpoint}`:** Gauge of uptime (100 for success, 0 for failure).
- **Screenshot:**
    - App Metrics
    ![Metrics](./screenshots/App%20metrics.png)

## Prometheus
Prometheus scrapes `/metrics` and monitors the app:
- **Target Health:** Prometheus Target Health
- **Alerts:** Defined in `deploy/prometheus/alert-rules.yaml` for high latency, error rate, and uptime issues.
- **Screenshots:**
    - Target Health
    ![TargetHealth](./screenshots/Prometheus%20Time%20Series%20Collection%20and%20Processing%20Server.png)
    - Alerts
    ![Alerts](./screenshots/Prometheus%20Time%20Series%20Collection%20and%20Processing%20Server%20-%20Alerts.png)

## Grafana
Grafana provides dashboards and alerting:
- **Dashboards:** Visualizes latency, request rate, error rate and uptime. Import `latency-dashboard-final.json`.
- **Alerts:** Configured to send notifications to Slack on thresholds (e.g., latency >1s).
- **Screenshots:**
    - Dashboards
    ![Dashboards](./screenshots/API%20Latency%20Monitor%20-%20Dashboards%20-%20Grafana.png)
    - Alert Rules
    ![GrafanaAlerts](./screenshots/Alert%20rules%20-%20Alerting%20-%20Grafana.png)
    - Slack Alert
    ![SlackAlert](./screenshots/Alert%20Slack%20notification%20-%20Alerts%20-%20Alerting%20-%20Grafana.png)
    - Slack Message
    ![SlackMessage](./screenshots/Slack%20Channel%20Notifications.png)

## Jaeger
Jaeger for distributed tracing:
- Traces API polls and internal operations.
- Jaeger UI
![Jaeger](./screenshots/Jaeger%20UI.png)

## CI/CD
Github Actions Workflows:
- **ci:** Builds and pushes Docker image on `src/**` changes.
- **Python Application:** Runs test and lint on pull requests
- **Screenshots:**
    - Github Actions
    ![GithubActions](./screenshots/Github%20Actions.png)

## Ansible
Automates deployment
- `infra.yaml`: Applies manifests and creates secrets from `.env`.
- Example Output:
    ```shell
    (.venv) rocorder@IBM-PF5ELEAQ:~/Github/api-latency-monitor$ ansible-playbook -i ansible_quickstart/inventory.ini ansible_quickstart/infra.yaml

    PLAY [Apply All configurations in Minikube and create Secret] *****************************************************************************************************************************

    TASK [Gathering Facts] ********************************************************************************************************************************************************************
    [WARNING]: Platform linux on host 127.0.0.1 is using the discovered Python interpreter at /home/rocorder/Github/api-latency-monitor/src/.venv/bin/python3.12, but future installation of
    another Python interpreter could change the meaning of that path. See https://docs.ansible.com/ansible-core/2.18/reference_appendices/interpreter_discovery.html for more information.
    ok: [127.0.0.1]

    TASK [Ensure log directory exists in Minikube] ********************************************************************************************************************************************
    changed: [127.0.0.1]

    TASK [Change permissions for log directory] ***********************************************************************************************************************************************
    changed: [127.0.0.1]

    TASK [Apply All configurations] ***********************************************************************************************************************************************************
    changed: [127.0.0.1]

    TASK [Delete api-token secret if it exists] ***********************************************************************************************************************************************
    changed: [127.0.0.1]

    TASK [Delete slack-webhook secret if it exists] *******************************************************************************************************************************************
    changed: [127.0.0.1]

    TASK [Wait for deletion to complete] ******************************************************************************************************************************************************
    ok: [127.0.0.1]

    TASK [Read API_TOKEN from .env file] ******************************************************************************************************************************************************
    changed: [127.0.0.1]

    TASK [Read SLACK_WEBHOOK_URL from .env file] **********************************************************************************************************************************************
    changed: [127.0.0.1]

    TASK [Create api-token secret] ************************************************************************************************************************************************************
    changed: [127.0.0.1]

    TASK [Create slack-webhook secret] ********************************************************************************************************************************************************
    changed: [127.0.0.1]

    TASK [Display kubectl apply output] *******************************************************************************************************************************************************
    ok: [127.0.0.1] => {
        "apply_result.stdout_lines": [
            "deployment.apps/alertmanager unchanged",
            "service/alertmanager unchanged",
            "configmap/alertmanager-config unchanged",
            "daemonset.apps/cadvisor configured",
            "configmap/monitoring-project unchanged",
            "namespace/monitoring-project unchanged",
            "deployment.apps/api-latency-monitor unchanged",
            "persistentvolumeclaim/log-pvc unchanged",
            "configmap/loki-config created",
            "deployment.apps/loki created",
            "service/loki created",
            "namespace/monitoring-project unchanged",
            "deployment.apps/grafana-deployment unchanged",
            "service/grafana-service unchanged",
            "configmap/grafana-datasources-config unchanged",
            "configmap/grafana-dashboards-config unchanged",
            "deployment.apps/jaeger unchanged",
            "service/jaeger unchanged",
            "service/jaeger-service unchanged",
            "namespace/opentelemetry unchanged",
            "deployment.apps/otel-collector unchanged",
            "configmap/otel-config unchanged",
            "service/otel-collector unchanged",
            "configmap/prometheus-alert-rules unchanged",
            "clusterrole.rbac.authorization.k8s.io/prometheus-pod-reader-cluster unchanged",
            "clusterrolebinding.rbac.authorization.k8s.io/prometheus-pod-reader-binding-cluster unchanged",
            "namespace/monitoring-project unchanged",
            "configmap/api-latency-monitor-prometheus-config unchanged",
            "deployment.apps/api-latency-monitor-prometheus-deployment unchanged",
            "service/api-latency-monitor-prometheus-service unchanged",
            "secret/api-token configured",
            "service/api-latency-monitor unchanged",
            "persistentvolume/log-pv-app-1 configured",
            "persistentvolume/log-pv-app-2 configured"
        ]
    }

    PLAY RECAP ********************************************************************************************************************************************************************************
    127.0.0.1                  : ok=12   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

    (.venv) rocorder@IBM-PF5ELEAQ:~/Github/api-latency-monitor$
    ```

## Testing
Run unit tests for polling logic:
```bash
pytest src/tests/test_poller.py
```

## Contributing
Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details on how to contribute to this project.

## License
This project is licensed under the MIT License - see [LICENSE](./LICENSE) for details.