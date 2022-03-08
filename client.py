import itertools
import json
from sys import stderr

import trio
from trio_websocket import open_websocket_url

from helpers import TIMEOUT, generate_bus_id, load_routes

ROUTE_BUS_AMOUNT = 3


async def run_bus(route, bus_number, ws):
    message = {
        'busId': generate_bus_id(route['name'], bus_number),
        'route': route['name'],
    }
    starting_coordinates_index = (
        bus_number * len(route['coordinates']) // ROUTE_BUS_AMOUNT
    )

    while True:
        for coordinates in itertools.chain(
            route['coordinates'][starting_coordinates_index:],
            route['coordinates'][:starting_coordinates_index],
        ):
            message.update({'lat': coordinates[0], 'lng': coordinates[1]})
            await ws.send_message(json.dumps(message, ensure_ascii=False))
            await trio.sleep(TIMEOUT)


async def launch_bus():
    try:
        async with open_websocket_url('ws://127.0.0.1:8080') as ws:
            async with trio.open_nursery() as nursery:
                for route in load_routes():
                    for bus_number in range(ROUTE_BUS_AMOUNT):
                        nursery.start_soon(run_bus, route, bus_number, ws)

    except OSError as ose:
        print('Connection attempt failed: %s' % ose, file=stderr)


if __name__ == '__main__':
    trio.run(launch_bus)
