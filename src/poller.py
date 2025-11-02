import requests
import time
from typing import Dict

async def poll_endpoints(endpoints: list, token: str) -> Dict:
    results = {}
    headers = {"Authorization": f"Bearer {token}"}
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(endpoint, headers=headers, timeout=5)
            latency = time.time() - start_time
            results[endpoint] = {
                "status_code": response.status_code,
                "latency": latency,
                "timestamp": time.time()
            }
        except requests.RequestException as e:
            results[endpoint] = {
                "status_code": 0,
                "latency": 0.0,
                "timestamp": time.time(),
                "error": str(e)
            }
    return results