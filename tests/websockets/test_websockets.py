import asyncio
import json

import pytest
from hamcrest import assert_that, has_entries, is_, equal_to
from hamcrest.core.core.future import future_raising, resolved
from starlette import status
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

    async def test_creating_order_via_http_receiving_messages_via_websocket(self, http_client, websocket_client):
        response = await http_client.post("/orders",
                                          json=OrderInput(stocks="EURUSD",
                                                          quantity=1000.24).model_dump())
        assert_that(response.status_code, equal_to(status.HTTP_201_CREATED), "Expected status is returned")
        expected_messages = [
            OrderOutput(id=response.json().get("id"),
                        stocks="EURUSD",
                        quantity=1000.24,
                        status=OrderStatus.pending),
            OrderOutput(id=response.json().get("id"),
                        stocks="EURUSD",
                        quantity=1000.24,
                        status=OrderStatus.executed),
            OrderOutput(id=response.json().get("id"),
                        stocks="EURUSD",
                        quantity=1000.24,
                        status=OrderStatus.cancelled)
        ]
        for expected_message in expected_messages:
            ws_message = await wait_for_response_and_parse_model(coro=websocket_client.recv(),
                                                                 timeout=TIMEOUT,
                                                                 model=OrderOutput)
            assert_that(ws_message, equal_to(expected_message), "Expected message is received")
