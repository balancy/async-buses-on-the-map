import json
import pickle

import pydantic
import pytest
import trio
from trio_websocket import open_websocket_url

test_client_data = [
    ('some message', json.JSONDecodeError),
    (
        '{"data":{"south_lat":55.727011350768876,'
        '"north_lat":55.78878211812553,"west_lng":37.56056785932743,'
        '"east_lng":37.670259479200475}}',
        pydantic.ValidationError,
    ),
    ('{"msgType":"newBounds"}', pydantic.ValidationError),
    (
        '{"msgType":"newBounds","data":{}}',
        pydantic.ValidationError,
    ),
    (
        '{"msgType":"newBounds","data":'
        '{"north_lat":55.78878211812553,"west_lng":37.56056785932743,'
        '"east_lng":37.670259479200475}}',
        pydantic.ValidationError,
    ),
]


@pytest.mark.parametrize('test_input,expected_value', test_client_data)
async def test_interaction_with_browser(test_input, expected_value):
    async def imitate_client():
        async with open_websocket_url('ws://127.0.0.1:8000') as ws:
            await ws.send_message(test_input)

            response = await ws.get_message()
            decoded_response = pickle.loads(response)

            assert type(decoded_response) == expected_value

    trio.run(imitate_client)
