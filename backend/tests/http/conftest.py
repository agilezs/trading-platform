import pytest_asyncio
from httpx import AsyncClient

from app.model.trading_platform_model import OrderOutput, OrderInput
from tests.conftest import get_http_url, wait_for_response_and_parse_model, TIMEOUT


@pytest_asyncio.fixture
async def http_client() -> AsyncClient:
    async with AsyncClient(base_url=get_http_url(),
                           headers={"Content-Type": "application/json"},
                           follow_redirects=True) as async_client:
        yield async_client


@pytest_asyncio.fixture
async def created_order(http_client) -> OrderOutput:
    response = await http_client.post("/orders",
                                      json=OrderInput(stocks="PLNUSD",
                                                      quantity=23.24).model_dump())
    yield OrderOutput.model_validate(response.json())
