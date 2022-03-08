import json
from itertools import chain, cycle
from random import choice
from sys import stderr

import trio
from trio_websocket import open_websocket_url

from helpers import TIMEOUT, generate_bus_id, load_routes

ROUTE_BUS_AMOUNT = 40
SOCKETS_AMOUNT = 10


async def run_bus(route, bus_number, send_channel):
    message = {
        'busId': generate_bus_id(route['name'], bus_number),
        'route': route['name'],
    }

    coordinates = route['coordinates']
    start_index = bus_number * len(coordinates) // ROUTE_BUS_AMOUNT
    bus_route = chain(coordinates[start_index:], coordinates[:start_index])

    for lat, lng in cycle(bus_route):
        message.update({'lat': lat, 'lng': lng})

        await send_channel.send(json.dumps(message, ensure_ascii=False))
        await trio.sleep(TIMEOUT)


async def send_updates(server_address, receive_channel):
    async with open_websocket_url(server_address) as ws:
        while True:
            try:
                async for message in receive_channel:
                    await ws.send_message(message)
            except OSError as ose:
                print('Connection attempt failed: %s' % ose, file=stderr)


async def launch_buses():
    channels = [trio.open_memory_channel(0) for _ in range(SOCKETS_AMOUNT)]

    async with trio.open_nursery() as nursery:
        for route in load_routes():
            send_channel, receive_channel = choice(channels)

            for bus_number in range(ROUTE_BUS_AMOUNT):
                nursery.start_soon(run_bus, route, bus_number, send_channel)

            nursery.start_soon(
                send_updates, 'ws://127.0.0.1:8080', receive_channel
            )


if __name__ == '__main__':
    trio.run(launch_buses)
