import json
from contextlib import suppress
from functools import partial

import trio
from trio_websocket import ConnectionClosed, serve_websocket

TIMEOUT = 0.1

buses = {}


async def listen_to_client(request):
    ws = await request.accept()
    while True:
        try:
            message = await ws.get_message()

            bus_info = json.loads(message)
            buses.update({bus_info['busId']: bus_info})
        except ConnectionClosed:
            break


async def talk_to_browser(request):
    ws = await request.accept()
    while True:
        try:
            message = {
                'msgType': 'Buses',
                'buses': [bus_info for bus_info in buses.values()],
            }
            await ws.send_message(json.dumps(message))
            await trio.sleep(TIMEOUT)
        except ConnectionClosed:
            break


async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(
            partial(
                serve_websocket,
                listen_to_client,
                '127.0.0.1',
                8080,
                ssl_context=None,
            ),
        ),
        nursery.start_soon(
            partial(
                serve_websocket,
                talk_to_browser,
                '127.0.0.1',
                8000,
                ssl_context=None,
            ),
        )


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        trio.run(main)
