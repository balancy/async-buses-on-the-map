import json
import logging
from contextlib import suppress
from functools import partial

import asyncclick as click
import trio
from pydantic.json import pydantic_encoder
from trio_websocket import ConnectionClosed, serve_websocket

from helper_classes import Bus, InvalidDataFormatException, WindowBounds

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
            bus = Bus.create_from(message)
            buses.update({bus.busId: bus})
        except InvalidDataFormatException as exc:
            exc_message, *_ = exc.args
            await ws.send_message(json.dumps(exc_message))
        except ConnectionClosed:
            break
        else:
            correct_response = {'msgType': 'Success', 'content': message}
            await ws.send_message(json.dumps(correct_response))


async def listen_to_browser(ws, window_bounds, verbose):
    while True:
        try:
            message = await ws.get_message()
            if verbose:
                logger.info(message)

            window_bounds.update_from_message(message)
        except InvalidDataFormatException as exc:
            exc_message, *_ = exc.args
            await ws.send_message(json.dumps(exc_message))
        except ConnectionClosed:
            break
        else:
            correct_response = {'msgType': 'Success', 'content': message}
            await ws.send_message(json.dumps(correct_response))


async def display_buses_in_browser(ws, window_bounds, verbose):
    while True:
        try:
            if window_bounds.are_set():
                visible_buses = find_buses_visible_in_browser(window_bounds)
                if verbose:
                    logger.info(f'{len(visible_buses)} buses visible')

                message = {
                    'msgType': 'Buses',
                    'buses': [bus for bus in visible_buses],
                }
                await ws.send_message(
                    json.dumps(message, default=pydantic_encoder)
                )
            await trio.sleep(TIMEOUT)
        except ConnectionClosed:
            break


async def interact_with_browser(request, verbose):
    ws = await request.accept()
    window_bounds = WindowBounds()

    async with trio.open_nursery() as nursery:
        nursery.start_soon(listen_to_browser, ws, window_bounds, verbose)
        nursery.start_soon(
            display_buses_in_browser, ws, window_bounds, verbose
        )


@click.command()
@click.option('--bus_port', default=8080, help='Port to listen client on')
@click.option('--verbose', default=False, help='Is logging enabled')
@click.option(
    '--browser_port', default=8000, help='Port to interact with browser on'
)
async def launch_server(bus_port, browser_port, verbose):
    async with trio.open_nursery() as nursery:
        nursery.start_soon(
            partial(
                serve_websocket,
                listen_to_client,
                '127.0.0.1',
                bus_port,
                ssl_context=None,
            ),
        ),
        nursery.start_soon(
            partial(
                serve_websocket,
                partial(
                    interact_with_browser,
                    verbose=verbose,
                ),
                '127.0.0.1',
                browser_port,
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
        launch_server(_anyio_backend='trio')
