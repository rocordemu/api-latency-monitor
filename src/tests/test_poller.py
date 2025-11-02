import pytest
from poller import poll_endpoints

@pytest.mark.asyncio
async def test_poll_endpoints():
    endpoints = ["https://httpbin.org/get"]
    results = await poll_endpoints(endpoints, token="")
    assert endpoints[0] in results
    assert "status_code" in results[endpoints[0]]
    assert "latency" in results[endpoints[0]]