import pytest
import sys
import os
import pytest-asyncio

current_dir = os.path.dirname(__file__)
print(current_dir)
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
print(parent_dir)
sys.path.append(parent_dir)
print(sys.path)
from poller import poll_endpoints

@pytest.mark.asyncio
async def test_poll_endpoints():
    endpoints = ["https://httpbin.org/get"]
    results = await poll_endpoints(endpoints, token="")
    assert endpoints[0] in results
    assert "status_code" in results[endpoints[0]]
    assert "latency" in results[endpoints[0]]
