import os

import pytest_asyncio
from httpx import AsyncClient


def get_http_url() -> str:
    host = os.getenv("FASTAPI_HTTP_HOST") or "http://localhost:8000"
    return host


def get_ws_url() -> str:
    host = os.getenv("FASTAPI_WS_HOST") or "ws://localhost:8000"
    return host


@pytest_asyncio.fixture
async def http_client() -> AsyncClient:
    async with AsyncClient(base_url=get_http_url(),
                           headers={"Content-Type": "application/json"},
                           follow_redirects=True) as async_client:
        yield async_client
