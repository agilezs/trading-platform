import uuid

import pytest
from hamcrest import assert_that, equal_to, has_entries, has_item, only_contains
from starlette import status

from tests.model.trading_platform_model import RequestError

pytestmark = pytest.mark.asyncio


class TestOrderRequestValidation:

    @pytest.mark.parametrize("method", ["GET", "DELETE"])
    async def test_manage_non_existing_order(self, method, http_client):
        # given
        non_existing_order_id = str(uuid.uuid4())
        # when
        response = await http_client.request(method=method,
                                             url=f"/orders/{non_existing_order_id}")
        # then
        assert_that(response.status_code, equal_to(status.HTTP_404_NOT_FOUND), "Order not found")
        assert_that(response.json(), has_entries(detail="Order not found!"))

    @pytest.mark.parametrize("desc,json_data,expected_errors", [
        ("empty body", {}, [RequestError(message="Field required",
                                         input={},
                                         localization=["body", "stocks"],
                                         type="missing"),
                            RequestError(message="Field required",
                                         input={},
                                         localization=["body", "quantity"],
                                         type="missing")]),
        ("missing required fields", {"any": "other"}, [RequestError(message="Field required",
                                                                    input={"any": "other"},
                                                                    localization=["body", "stocks"],
                                                                    type="missing"),
                                                       RequestError(message="Field required",
                                                                    input={"any": "other"},
                                                                    localization=["body", "quantity"],
                                                                    type="missing")]),
        ("required fields are null", {"stocks": None,
                                      "quantity": None}, [RequestError(message="Input should be a valid string",
                                                                       localization=["body", "stocks"],
                                                                       type="string_type"),
                                                          RequestError(message="Input should be a valid number",
                                                                       localization=["body",
                                                                                     "quantity"],
                                                                       type="float_type")]),
        ("stocks invalid type", {"stocks": 123,
                                 "quantity": 12.42}, [RequestError(message="Input should be a valid string",
                                                                   input=123,
                                                                   localization=["body", "stocks"],
                                                                   type="string_type")]),
        ("quantity invalid type", {"stocks": "EURPLN",
                                   "quantity": "test"}, [RequestError(message="Input should be a valid number, "
                                                                              "unable to parse string as a number",
                                                                      input="test",
                                                                      localization=["body", "quantity"],
                                                                      type="float_parsing")]),
        ("quantity as negative float", {"stocks": "EURUSD",
                                        "quantity": -0.242}, [RequestError(message="Input should be greater than 0",
                                                                           input=-0.242,
                                                                           localization=["body", "quantity"],
                                                                           type="greater_than")]),
        ("quantity as negative int", {"stocks": "EURUSD",
                                      "quantity": -100}, [RequestError(message="Input should be greater than 0",
                                                                       input=-100,
                                                                       localization=["body", "quantity"],
                                                                       type="greater_than")]),
        ("quantity as 0 float", {"stocks": "EURUSD",
                                 "quantity": 0.000}, [RequestError(message="Input should be greater than 0",
                                                                   input=0.0,
                                                                   localization=["body", "quantity"],
                                                                   type="greater_than")]),
        ("quantity as 0 int", {"stocks": "EURUSD",
                               "quantity": 0}, [RequestError(message="Input should be greater than 0",
                                                             input=0,
                                                             localization=["body", "quantity"],
                                                             type="greater_than")])
    ])
    async def test_invalid_order_request(self, desc, json_data, expected_errors, http_client):
        # when
        response = await http_client.post("/orders", json=json_data)
        # then
        assert_that(response.status_code, equal_to(status.HTTP_400_BAD_REQUEST), "Bad request properly handled")
        for error in expected_errors:
            assert_that(response.json().get("errors"),
                        has_item(error.model_dump(exclude_none=True)),
                        "Expected errors returned")

    async def test_invalid_json(self, http_client):
        # given
        broken_json_request = '{"stocks": "EURPLN" "quantity": 10}'
        # when
        response = await http_client.post("/orders", content=broken_json_request)
        # then
        expected_error = RequestError(message="JSON decode error",
                                      input={},
                                      localization=["body", 20],
                                      type="json_invalid").model_dump(exclude_none=True)
        assert_that(response.status_code, equal_to(status.HTTP_400_BAD_REQUEST), "Invalid json properly handled")
        assert_that(response.json().get("errors"), only_contains(expected_error), "Expected error returned")
