import json
import logging
from contextlib import suppress
from functools import partial

import trio
from trio_websocket import ConnectionClosed, serve_websocket

TIMEOUT = 0.1

buses = {}


def is_bus_inside_browser_window(bounds, lat, lng):
    return (
        bounds['south_lat'] < lat < bounds['north_lat']
        and bounds['west_lng'] < lng < bounds['east_lng']
    )


async def listen_to_client(request):
    ws = await request.accept()
    while True:
        try:
            message = await ws.get_message()

            bus_info = json.loads(message)
            buses.update({bus_info['busId']: bus_info})
        except ConnectionClosed:
            break


async def listen_to_browser(ws):
    while True:
        try:
            message = await ws.get_message()
            logger.info(message)

            window_bounds = json.loads(message)['data']

            visible_buses = [
                bus
                for bus in buses.values()
                if is_bus_inside_browser_window(
                    window_bounds, bus['lat'], bus['lng']
                )
            ]

            logger.info(f'{len(visible_buses)} inside window bounds')
        except ConnectionClosed:
            break


async def talk_to_browser(ws):
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


async def interact_with_browser(request):
    ws = await request.accept()
    async with trio.open_nursery() as nursery:
        nursery.start_soon(listen_to_browser, ws)
        nursery.start_soon(talk_to_browser, ws)


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
                interact_with_browser,
                '127.0.0.1',
                8000,
                ssl_context=None,
            ),
        )


if __name__ == '__main__':
    logging.basicConfig(
        format=u'%(levelname)s:server: %(message)s',
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    with suppress(KeyboardInterrupt):
        trio.run(main)
