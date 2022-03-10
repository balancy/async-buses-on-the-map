import json

import pytest
import trio
from trio_websocket import open_websocket_url

test_client_data = [
    ('some message', 'JSONDecodeError'),
    ('{"msgType":"newBounds"}', 'ValidationError'),
    ('{"msgType":"newBounds","data":1}', 'ValidationError'),
    (
        '{"data":{"south_lat":55.727011350768876,'
        '"north_lat":55.78878211812553,"west_lng":37.56056785932743,'
        '"east_lng":37.670259479200475}}',
        'ValidationError',
    ),
    ('{"msgType":"newBounds","data":{}}', 'ValidationError'),
    (
        '{"msgType":"newBounds","data":'
        '{"north_lat":"some_value","west_lng":37.56056785932743,'
        '"east_lng":37.670259479200475}}',
        'ValidationError',
    ),
    (
        '{"msgType":"newBounds","data":{"south_lat":55.727011350768876,'
        '"north_lat":55.78878211812553,"west_lng":37.56056785932743,'
        '"east_lng":37.670259479200475}}',
        'Success',
    ),
]


@pytest.mark.parametrize('test_input,expected_value', test_client_data)
async def test_interaction_with_browser(test_input, expected_value):
    async def imitate_client():
        async with open_websocket_url('ws://127.0.0.1:8000') as ws:
            await ws.send_message(test_input)

            response = await ws.get_message()
            decoded_response = json.loads(response)

            assert expected_value == decoded_response['msgType']

    trio.run(imitate_client)


test_bus_data = [
    ('some message', 'JSONDecodeError'),
    (
        '{"busId": "a1-0", "route": "a1", "lat": 12}',
        'ValidationError',
    ),
    (
        '{"busId": "a1-0", "route": "a1", "lat": 12, "lng": "something"}',
        'ValidationError',
    ),
    (
        '{"busId": "a1-0", "route": "a1", "lat": 12, "lng": 13}',
        'Success',
    ),
]


@pytest.mark.parametrize('test_input,expected_value', test_bus_data)
async def test_interaction_with_buses(test_input, expected_value):
    async def imitate_buses_launch():
        async with open_websocket_url('ws://127.0.0.1:8080') as ws:
            await ws.send_message(test_input)

            response = await ws.get_message()
            decoded_response = json.loads(response)

            assert expected_value == decoded_response['msgType']

    trio.run(imitate_buses_launch)
