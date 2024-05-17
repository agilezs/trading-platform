import asyncio
from typing import Coroutine, Type

import pytest_asyncio
import websockets
from pydantic import BaseModel

from tests.conftest import get_ws_url

TIMEOUT = 5  # seconds


async def wait_for_response_and_parse_model(coro: Coroutine, timeout: int, model: Type[BaseModel]) -> BaseModel:
    response = await asyncio.wait_for(coro, timeout=timeout)
    return model.model_validate_json(response)


#
# @pytest_asyncio.fixture(scope="session")
# async def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


@pytest_asyncio.fixture
async def websocket_client():
    uri = get_ws_url() + "/ws"
    async with websockets.connect(uri) as websocket:
        yield websocket


@pytest_asyncio.fixture
async def second_websocket_client():
    uri = get_ws_url() + "/ws"
    async with websockets.connect(uri) as websocket:
        yield websocket


@pytest_asyncio.fixture
async def third_websocket_client():
    uri = get_ws_url() + "/ws"
    async with websockets.connect(uri) as websocket:
        yield websocket
