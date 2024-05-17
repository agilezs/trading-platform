import pytest
from hamcrest import assert_that, equal_to, has_entries, is_, empty
from starlette import status

from tests.model.trading_platform_model import OrderInput, OrderStatus

pytestmark = pytest.mark.asyncio


class TestOrderRoutes:

    @pytest.mark.parametrize("method,endpoint_path,data", [
        ("GET", "/orders", None),
        ("POST", "/orders", OrderInput(stocks="EURPLN", quantity=2.0).model_dump()),
        ("GET", "orders/{order_id}", None),
        ("DELETE", "orders/{order_id}", None)
    ])
    async def test_route_exists(self, method, endpoint_path, data, http_client, created_order):
        if "order_id" in endpoint_path:
            endpoint_path = endpoint_path.format(order_id=created_order.id)
        response = await http_client.request(method=method,
                                             url=endpoint_path,
                                             json=data)
        assert_that(response.status_code != status.HTTP_404_NOT_FOUND)

    async def test_get_orders(self, http_client):
        response = await http_client.get("/orders")
        assert_that(response.status_code, equal_to(status.HTTP_200_OK), "Response status is 200")
        assert_that(isinstance(response.json(), list), "The response is a list")

    async def test_place_order(self, http_client):
        order_request = OrderInput(stocks="EURUSD", quantity=100)
        response = await http_client.post("/orders", json=order_request.model_dump())
        assert_that(response.status_code, equal_to(status.HTTP_201_CREATED), "Response status is 201")
        assert_that(response.json(), has_entries(status=OrderStatus.pending.value,
                                                 stocks=order_request.stocks,
                                                 quantity=order_request.quantity), "Client received expected data")

    async def test_get_order(self, http_client, created_order):
        response = await http_client.get(f"/orders/{created_order.id}")
        assert_that(response.status_code, equal_to(status.HTTP_200_OK), "Response status is 200")
        assert_that(response.json(), equal_to(created_order.model_dump()), "Returned order is equal to created")

    async def test_cancel_order(self, http_client, created_order):
        response = await http_client.delete(f"/orders/{created_order.id}")
        assert_that(response.status_code, equal_to(status.HTTP_204_NO_CONTENT), "Response status is 200")
        assert_that(response.text, is_(empty()))
