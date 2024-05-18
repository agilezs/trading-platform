import asyncio
import json

import pytest
from hamcrest import assert_that, has_entries, is_
from hamcrest.core.core.future import future_raising, resolved
from websockets.legacy.client import WebSocketClientProtocol

from tests.model.trading_platform_model import OrderOutput, OrderStatus, OrderInput
from tests.websockets.conftest import wait_for_response_and_parse_model, TIMEOUT

pytestmark = pytest.mark.asyncio


class TestWsMessages:
    async def test_client_gets_status_update_messages_in_correct_order(self, websocket_client: WebSocketClientProtocol):
        # given
        await websocket_client.send(OrderInput(stocks="USDPLN", quantity=12.52).model_dump_json())
        for order_status in [OrderStatus.pending, OrderStatus.executed, OrderStatus.cancelled]:
            # when
            response = await wait_for_response_and_parse_model(coro=websocket_client.recv(),
                                                               timeout=TIMEOUT,
                                                               model=OrderOutput)
            # then
            assert_that(isinstance(response, OrderOutput), "Response parsed without errors")
            assert_that(response.model_dump(),
                        matcher=has_entries(status=order_status.value),
                        reason=f"Client received expected message with status '{order_status}'")
            assert_that(websocket_client.closed,
                        matcher=is_(False),
                        reason="Client is connected")

    async def test_multiple_clients_get_broadcast_messages(self,
                                                           websocket_client,
                                                           second_websocket_client,
                                                           third_websocket_client):
        # given
        await websocket_client.send(json.dumps({"stocks": "EURUSD", "quantity": 10}))
        for order_status in [OrderStatus.pending, OrderStatus.executed, OrderStatus.cancelled]:
            # when
            response = await wait_for_response_and_parse_model(coro=websocket_client.recv(),
                                                               timeout=TIMEOUT,
                                                               model=OrderOutput)
            second_response = await wait_for_response_and_parse_model(coro=second_websocket_client.recv(),
                                                                      timeout=TIMEOUT,
                                                                      model=OrderOutput)
            third_response = await wait_for_response_and_parse_model(coro=third_websocket_client.recv(),
                                                                     timeout=TIMEOUT,
                                                                     model=OrderOutput)
            # then
            assert_that(response.model_dump(),
                        matcher=has_entries(stocks="EURUSD",
                                            quantity=10,
                                            status=order_status.value),
                        reason=f"Client received expected message with status '{order_status}'")
            assert_that(response == second_response == third_response,
                        reason="All connected clients received expected message")

    async def test_no_more_messages_are_received_after_cancelled_status(self,
                                                                        websocket_client,
                                                                        second_websocket_client,
                                                                        third_websocket_client):
        # given
        await websocket_client.send(OrderInput(stocks="USDPLN", quantity=5).model_dump_json())
        for order_status in [OrderStatus.pending, OrderStatus.executed, OrderStatus.cancelled]:
            # when
            response = await wait_for_response_and_parse_model(coro=websocket_client.recv(),
                                                               timeout=TIMEOUT,
                                                               model=OrderOutput)
            second_response = await wait_for_response_and_parse_model(coro=second_websocket_client.recv(),
                                                                      timeout=TIMEOUT,
                                                                      model=OrderOutput)
            third_response = await wait_for_response_and_parse_model(coro=third_websocket_client.recv(),
                                                                     timeout=TIMEOUT,
                                                                     model=OrderOutput)
            # then
            assert_that(response.model_dump(),
                        matcher=has_entries(stocks="USDPLN",
                                            quantity=5,
                                            status=order_status.value),
                        reason=f"Client received expected message with status '{order_status}'")
            assert_that(response == second_response == third_response,
                        reason="All connected clients received expected message")
        # check if there is no more left messages
        assert_that(await resolved(asyncio.wait_for(websocket_client.recv(), timeout=TIMEOUT)),
                    future_raising(TimeoutError),
                    "No more messages left")
        assert_that(await resolved(asyncio.wait_for(second_websocket_client.recv(), timeout=TIMEOUT)),
                    future_raising(TimeoutError),
                    "No more messages left")
        assert_that(await resolved(asyncio.wait_for(third_websocket_client.recv(), timeout=TIMEOUT)),
                    future_raising(TimeoutError),
                    "No more messages left")
