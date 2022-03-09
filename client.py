import json
import logging
from contextlib import suppress
from itertools import chain, cycle
from random import choice, randint

import asyncclick as click
import trio
from trio_websocket import open_websocket_url

from helpers import generate_bus_id, load_routes, relaunch_on_disconnect


async def run_bus(route, bus_number, send_channel, prefix, timeout):
    prefix = f'{prefix}-' if prefix else prefix
    message = {
        'busId': generate_bus_id(f"{prefix}{route['name']}", bus_number),
        'route': route['name'],
    }

    coords = route['coordinates']
    start_index = randint(0, len(coords) - 1)
    bus_route = chain(coords[start_index:], coords[:start_index])

    for lat, lng in cycle(bus_route):
        message.update({'lat': lat, 'lng': lng})
        await send_channel.send(json.dumps(message, ensure_ascii=False))
        await trio.sleep(timeout)


@relaunch_on_disconnect
async def send_updates(server_address, receive_channel, logging_enabled):
    async with open_websocket_url(server_address) as ws:
        async for message in receive_channel:
            if logging_enabled:
                logger.info(message)
            await ws.send_message(message)


@click.command()
@click.option('--server', default='ws://127.0.0.1:8080', help='Server address')
@click.option('--routes_amount', default=595, help='Amount of bus routes')
@click.option('--buses_per_route', default=5, help='Amount of buses per route')
@click.option('--sockets_amount', default=10, help='Amount of websockets')
@click.option('--emulator_id', default='', help='Prefix for busId')
@click.option('--timeout', default=0.5, help='Refresh timeout for coordinates')
@click.option('--logging_enabled', default=False, help='Is logging enabled?')
async def launch_buses(
    server,
    routes_amount,
    buses_per_route,
    sockets_amount,
    emulator_id,
    timeout,
    logging_enabled,
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
                logging_enabled,
            )


if __name__ == '__main__':
    logging.basicConfig(
        format=u'[%(asctime)s] %(levelname)s: %(message)s',
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    with suppress(KeyboardInterrupt):
        launch_buses(_anyio_backend='trio')
