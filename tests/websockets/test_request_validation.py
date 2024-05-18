import json

import pytest
from hamcrest import assert_that, equal_to, has_length
from starlette import status

from tests.model.trading_platform_model import Error, RequestError, RequestErrors
from tests.websockets.conftest import wait_for_response_and_parse_model, TIMEOUT

pytestmark = pytest.mark.asyncio

request_validation_data = [
    ("empty request", {}, [
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Field required",
                     input={},
                     localization=["stocks"],
                     type="missing"),
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Field required",
                     input={},
                     localization=["quantity"],
                     type="missing")
    ]),
    ("request not validated", {"test": "data"}, [
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Field required",
                     input={"test": "data"},
                     localization=["stocks"],
                     type="missing"),
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Field required",
                     input={"test": "data"},
                     localization=["quantity"],
                     type="missing")
    ]),
    ("quantity missing in request", {"stocks": "EURPLN"}, [
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Field required",
                     input={"stocks": "EURPLN"},
                     localization=["quantity"],
                     type="missing")
    ]),
    ("stocks missing in request", {"quantity": 2}, [
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Field required",
                     input={"quantity": 2},
                     localization=["stocks"],
                     type="missing")
    ]),
    ("wrong stocks type", {"stocks": 123, "quantity": 10}, [
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Input should be a valid string",
                     input=123,
                     localization=["stocks"],
                     type="string_type")
    ]),
    ("wrong quantity type", {"stocks": "EURGBP", "quantity": "abc"}, [
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Input should be a valid number, unable to parse string as a number",
                     input="abc",
                     localization=["quantity"],
                     type="float_parsing")
    ]),
    ("wrong quantity type", {"stocks": "EURGBP", "quantity": None}, [
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Input should be a valid number",
                     input=None,
                     localization=["quantity"],
                     type="float_type")
    ]),
    ("quantity as negative float amount", {"stocks": "GBPPLN", "quantity": -0.245}, [
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Input should be greater than 0",
                     input=-0.245,
                     localization=["quantity"],
                     type="greater_than")
    ]),
    ("quantity as negative int amount", {"stocks": "GBPPLN", "quantity": -1}, [
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Input should be greater than 0",
                     input=-1,
                     localization=["quantity"],
                     type="greater_than")
    ]),
    ("quantity as float zero", {"stocks": "USDAUD", "quantity": 0.00}, [
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Input should be greater than 0",
                     input=0.0,
                     localization=["quantity"],
                     type="greater_than")
    ]),
    ("quantity as int zero", {"stocks": "USDAUD", "quantity": 0}, [
        RequestError(code=status.WS_1003_UNSUPPORTED_DATA,
                     message="Input should be greater than 0",
                     input=0,
                     localization=["quantity"],
                     type="greater_than")
    ]),
]


class TestWsRequestValidation:

    @pytest.mark.parametrize("desc,json_data,expected_errors", request_validation_data)
    async def test_request_validation_errors(self, desc, json_data, expected_errors, websocket_client):
        # given
        await websocket_client.send(json.dumps(json_data))

        # when
        response = await wait_for_response_and_parse_model(coro=websocket_client.recv(),
                                                           timeout=TIMEOUT,
                                                           model=RequestErrors)
        # then
        assert_that(response.errors, has_length(len(expected_errors)), "Same error count")
        for returned_error, expected_error in zip(response.errors, expected_errors):
            assert_that(returned_error, equal_to(expected_error), "Error as expected")

    async def test_invalid_json(self, websocket_client):
        # given
        await websocket_client.send('{"stocks": "EURUSD" "quantity": 10.0}')
        # when
        response = await wait_for_response_and_parse_model(coro=websocket_client.recv(),
                                                           timeout=TIMEOUT,
                                                           model=RequestErrors)
        # then
        assert_that(response.errors, has_length(1), "One error returned")
        assert_that(response.errors[0], equal_to(Error(code=status.WS_1003_UNSUPPORTED_DATA,
                                                       message="Expecting ',' delimiter: line 1 column 21 (char 20)")))
