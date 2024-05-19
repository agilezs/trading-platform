import pytest_asyncio

from tests.model.trading_platform_model import OrderOutput, OrderInput
from tests.conftest import http_client


@pytest_asyncio.fixture
async def created_order(http_client) -> OrderOutput:
    response = await http_client.post("/orders",
                                      json=OrderInput(stocks="PLNUSD",
                                                      quantity=23.24).model_dump())
    yield OrderOutput.model_validate(response.json())
