import functools
import json
import logging
import os
from contextlib import suppress

# from dataclasses import asdict
from itertools import chain, cycle
from random import choice, randint

import asyncclick as click
import trio
from pydantic.json import pydantic_encoder
from trio_websocket import ConnectionClosed, HandshakeError, open_websocket_url

from helper_classes import Bus

RECONNECTION_TIMEOUT = 5


def load_routes(routes_amount, directory_path='routes'):
    for filename in os.listdir(directory_path)[: routes_amount + 1]:
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf8') as file:
                yield json.load(file)


def generate_bus_id(route_id, bus_index):
    return f"{route_id}-{bus_index}"


def relaunch_on_disconnect(async_function):
    @functools.wraps(async_function)
    async def wrapper(*args, **kwargs):
        while True:
            try:
                return await async_function(*args, **kwargs)
            except (ConnectionClosed, HandshakeError):
                logger.error('Connection lost. Trying to reconnect ...')
                await trio.sleep(RECONNECTION_TIMEOUT)

    return wrapper


async def run_bus(route, bus_number, send_channel, emulator_id, timeout):
    emulator_id = f'{emulator_id}-' if emulator_id else emulator_id
    bus_id = generate_bus_id(f"{emulator_id}{route['name']}", bus_number)
    bus = Bus(bus_id, route['name'])

    coordinates = route['coordinates']
    start_index = randint(0, len(coordinates) - 1)
    bus_route = chain(coordinates[start_index:], coordinates[:start_index])

    for lat, lng in cycle(bus_route):
        bus.update_coordinates(lat, lng)
        await send_channel.send(
            json.dumps(bus, ensure_ascii=False, default=pydantic_encoder)
        )
        await trio.sleep(timeout)


@relaunch_on_disconnect
async def send_updates(server_address, receive_channel, verbose):
    async with open_websocket_url(server_address) as ws:
        async for message in receive_channel:
            if verbose:
                logger.info(message)
            await ws.send_message(message)


@click.command()
@click.option('--server', default='ws://127.0.0.1:8080', help='Server address')
@click.option('--routes_amount', default=595, help='Amount of bus routes')
@click.option('--buses_per_route', default=5, help='Amount of buses per route')
@click.option('--sockets_amount', default=10, help='Amount of websockets')
@click.option('--emulator_id', default='', help='Prefix for busId')
@click.option('--timeout', default=0.5, help='Refresh timeout for coordinates')
@click.option('--verbose', default=False)
async def launch_buses(
    server,
    routes_amount,
    buses_per_route,
    sockets_amount,
    emulator_id,
    timeout,
    verbose,
):
    channels = [trio.open_memory_channel(0) for _ in range(sockets_amount)]

    async with trio.open_nursery() as nursery:
        for route in load_routes(routes_amount):
            send_channel, receive_channel = choice(channels)

            for bus_number in range(buses_per_route):
                nursery.start_soon(
                    run_bus,
                    route,
                    bus_number,
                    send_channel,
                    emulator_id,
                    timeout,
                )

            nursery.start_soon(
                send_updates,
                server,
                receive_channel,
                verbose,
            )


if __name__ == '__main__':
    logging.basicConfig(
        format=u'%(levelname)s:client: %(message)s',
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    with suppress(KeyboardInterrupt):
        launch_buses(_anyio_backend='trio')
