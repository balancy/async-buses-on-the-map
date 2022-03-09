import json
import logging
from contextlib import suppress
from dataclasses import asdict
from functools import partial

import trio
from trio_websocket import ConnectionClosed, serve_websocket

from helper_classes import Bus, WindowBounds

TIMEOUT = 0.5

buses = {}


def is_bus_inside_browser_window(bounds, bus):
    return (
        bounds.south_lat < bus.lat < bounds.north_lat
        and bounds.west_lng < bus.lng < bounds.east_lng
    )


def find_buses_visible_in_browser(bounds):
    visible_buses = [
        bus
        for bus in buses.values()
        if is_bus_inside_browser_window(bounds, bus)
    ]
    return visible_buses


async def listen_to_client(request):
    ws = await request.accept()
    while True:
        try:
            message = await ws.get_message()

            bus = Bus(**json.loads(message))
            buses.update({bus.busId: bus})
        except ConnectionClosed:
            break


async def listen_to_browser(ws, window_bounds):
    while True:
        try:
            message = await ws.get_message()
            logger.info(message)

            window_bounds.update(**json.loads(message)['data'])
        except ConnectionClosed:
            break


async def display_buses_in_browser(ws, window_bounds):
    while True:
        try:
            if window_bounds.are_set():
                visible_buses = find_buses_visible_in_browser(window_bounds)
                message = {
                    'msgType': 'Buses',
                    'buses': [asdict(bus) for bus in visible_buses],
                }
                logger.info(f'There are {len(visible_buses)} visible buses')
                await ws.send_message(json.dumps(message))
            await trio.sleep(TIMEOUT)
        except ConnectionClosed:
            break


async def interact_with_browser(request):
    ws = await request.accept()
    window_bounds = WindowBounds()

    async with trio.open_nursery() as nursery:
        nursery.start_soon(listen_to_browser, ws, window_bounds)
        nursery.start_soon(display_buses_in_browser, ws, window_bounds)


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
