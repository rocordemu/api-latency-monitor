# API Latency Monitor

Monitors latency and availability of `/appRunning` endpoints for three IBM Cloud applications, with Prometheus metrics and Grafana dashboards.

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
1. Start Minikube: `minikube start --driver=docker`
2. Build Docker image: `docker build -t your-docker-repo/api-latency-monitor:latest .`
   - Note: `.dockerignore` excludes `src/.env`, `src/.venv`, and other temporary files.
3. Push image: `docker push your-docker-repo/api-latency-monitor:latest`
4. Create Secret: `kubectl create secret generic api-token --from-literal=token=$(grep API_TOKEN src/.env | cut -d '=' -f2 | tr -d ' \t\r\n') -n monitoring-project`
5. Create Secret: `kubectl create secret generic slack-webhook --from-literal=token=$(grep SLACK_WEBHOOK_URL src/.env | cut -d '=' -f2 | tr -d ' \t\r\n') -n monitoring-project`
5. Apply manifests: `kubectl apply -f deploy/ -R`
6. Access service: `minikube service api-latency-monitor -n monitoring-project`

    ### Ansible
    - Run playbook: `ansible-playbook -i ansible_quickstart/inventory.ini ansible_quickstart/infra.yaml`

## Configuration
- **Local**: Environment variables are loaded from `src/.env` using `python-dotenv`.
- **Kubernetes**: Variables are injected from `deploy/configmap.yaml` (API_URL_1, API_URL_2, API_URL_3, POLL_INTERVAL) and `deploy/secret.yaml` (API_TOKEN, SLACK_WEBHOOK_URL).
- `POLL_INTERVAL`: Polling frequency in seconds (default: 60).
- Note: `src/.env` and `src/.venv` are not included in the Docker image (excluded by `.dockerignore`).

## Kubernetes
This application creates the namespace `monitoring-project` and produces Deployments, Pods, Services, Config Maps and Secrets.
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

## Application Metrics
The application generates the following metrics which then we will monitor them from Prometheus and Grafana.
![Metrics](./screenshots/App%20metrics.png)

## Prometheus
This application uses Prometheus for monitoring and scraping metrics from the `/metrics` endpoint.
- Target Health
![TargetHealth](./screenshots/Prometheus%20Time%20Series%20Collection%20and%20Processing%20Server.png)
- Alerts
![Alerts](./screenshots/Prometheus%20Time%20Series%20Collection%20and%20Processing%20Server%20-%20Alerts.png)

## Grafana
This application uses Grafana for monitoring with dashboards and sending alerts through Slack.
- Dashboards
![Dashboards](./screenshots/API%20Latency%20Monitor%20-%20Dashboards%20-%20Grafana.png)
- Alerts
![GrafanaAlerts](./screenshots/Alert%20rules%20-%20Alerting%20-%20Grafana.png)
- Slack Alert
![SlackAlert](./screenshots/Alert%20Slack%20notification%20-%20Alerts%20-%20Alerting%20-%20Grafana.png)
- Slack Message
![SlackMessage](./screenshots/Slack%20Channel%20Notifications.png)

## Jaeger
This application uses Jaeger for traces.
![Jaeger](./screenshots/Jaeger%20UI.png)

## CI/CD
For CI/CD, this application has 2 workflows. `ci` workflow pushes the changes in `src/**` to a new docker image with the _latest_ tag. `Python Application` workflow runs tests and lint on the same directory where all the python scripts are stored.
![GithubActions](./screenshots/Github%20Actions.png)

## Ansible
To apply all `.yaml` files and configure the environment for the container app, we created an ansible playbook. Here is an example of the output:
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
Run tests: `pytest src/tests/test_poller.py`