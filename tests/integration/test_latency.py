# pyright: reportCallIssue=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportMissingParameterType=false

import pytest
from httpx import AsyncClient
from src.inference.api.server import app


@pytest.mark.asyncio
async def test_health_latency(benchmark):
    async def call():
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            resp = await client.get("/api/health")
            assert resp.status_code == 200
    # 측정 반복: 50회 요청, 5 라운드
    benchmark.pedantic(call, iterations=50, rounds=5)


@pytest.mark.asyncio
async def test_clear_cache_latency(benchmark):
    async def call():
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            resp = await client.post("/api/clear_cache")
            assert resp.status_code == 200
    # 측정 반복: 20회 요청, 5 라운드
    benchmark.pedantic(call, iterations=20, rounds=5)
