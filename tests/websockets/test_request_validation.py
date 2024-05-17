import json

import pytest
from hamcrest import assert_that, equal_to, contains_string
from starlette import status

from tests.model.trading_platform_model import Error
from tests.websockets.conftest import wait_for_response_and_parse_model, TIMEOUT


def create_required_field_missing_error_message(input_value, *invalid_fields):
    invalid_field_desc = []
    for invalid_field in invalid_fields:
        invalid_field_desc.append(
            f"""{invalid_field}
  Field required [type=missing, input_value={input_value}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.7/v/missing""")
    return invalid_field_desc


missing_required_fields_data = [
    ("empty request", {}, ["stocks", "quantity"]),
    ("request not validated", {"test": "data"}, ["stocks", "quantity"]),
    ("quantity missing in request", {"stocks": "EURPLN"}, ["quantity"]),
    ("stocks missing in request", {"quantity": 2}, ["stocks"]),
]

wrong_field_type_data = [
    ("wrong stocks type", {"stocks": 123, "quantity": 10},
     "stocks\n  Input should be a valid string [type=string_type, input_value=123, input_type=int]"),
    ("wrong quantity type", {"stocks": "EURGBP", "quantity": "abc"},
     "quantity\n  Input should be a valid number, unable to parse string as a number "
     "[type=float_parsing, input_value='abc', input_type=str]"),
    ("wrong quantity type", {"stocks": "EURGBP", "quantity": None},
     "quantity\n  Input should be a valid number [type=float_type, input_value=None, input_type=NoneType]"),
]

wrong_field_value_data = [
    ("quantity as negative float amount", {"stocks": "GBPPLN", "quantity": -0.245}),
    ("quantity as negative int amount", {"stocks": "GBPPLN", "quantity": -1}),
    ("quantity as float zero", {"stocks": "USDAUD", "quantity": 0.00}),
    ("quantity as int zero", {"stocks": "USDAUD", "quantity": 0}),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("desc,json_data,invalid_fields", missing_required_fields_data)
async def test_request_required_field_missing(desc, json_data, invalid_fields, websocket_client):
    # given
    await websocket_client.send(json.dumps(json_data))

    # when
    response = await wait_for_response_and_parse_model(coro=websocket_client.recv(),
                                                       timeout=TIMEOUT,
                                                       model=Error)
    # then
    assert_that(response.code, equal_to(status.WS_1003_UNSUPPORTED_DATA), "Returned error code is UNSUPPORTED_DATA")
    for error_message in create_required_field_missing_error_message(json_data, *invalid_fields):
        assert_that(response.message, contains_string(error_message), "Error response contains expected message")


@pytest.mark.asyncio
@pytest.mark.parametrize("desc,json_data,error_message", wrong_field_type_data)
async def test_request_required_field_wrong_type(desc, json_data, error_message, websocket_client):
    # given
    await websocket_client.send(json.dumps(json_data))

    # when
    response = await wait_for_response_and_parse_model(coro=websocket_client.recv(),
                                                       timeout=TIMEOUT,
                                                       model=Error)
    # then
    assert_that(response.code, equal_to(status.WS_1003_UNSUPPORTED_DATA), "Returned error code is UNSUPPORTED_DATA")
    assert_that(response.message, contains_string(error_message), "Error response contains expected message")


@pytest.mark.asyncio
@pytest.mark.parametrize("desc,json_data", wrong_field_value_data)
async def test_request_required_field_wrong_value(desc, json_data, websocket_client):
    # given
    expected_error_message = "Input should be greater than 0 [type=greater_than, input_value={0}, input_type={1}]"
    quantity = json_data.get("quantity")
    await websocket_client.send(json.dumps(json_data))

    # when
    response = await wait_for_response_and_parse_model(coro=websocket_client.recv(),
                                                       timeout=TIMEOUT,
                                                       model=Error)
    # then
    assert_that(response.code, equal_to(status.WS_1003_UNSUPPORTED_DATA), "Returned error code is UNSUPPORTED_DATA")
    assert_that(response.message,
                contains_string(expected_error_message.format(quantity, type(quantity).__name__)),
                "Error response contains expected message")
