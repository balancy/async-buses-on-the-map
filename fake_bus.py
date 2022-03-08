import json
from sys import stderr

import trio
from trio_websocket import open_websocket_url

from load_routes import load_routes

TIMEOUT = 1


async def run_bus(route, ws):
    message = {
        'msgType': 'Buses',
        'buses': [
            {
                'busId': f'{route["name"]}-0',
                'route': route['name'],
            },
        ],
    }
    for coordinates in route['coordinates']:
        message['buses'][0].update(
            {'lat': coordinates[0], 'lng': coordinates[1]}
        )
        await ws.send_message(json.dumps(message, ensure_ascii=False))
        await trio.sleep(TIMEOUT)


async def launch_bus():
    try:
        async with open_websocket_url('ws://127.0.0.1:8080') as ws:
            async with trio.open_nursery() as nursery:
                for route in load_routes():
                    nursery.start_soon(run_bus, route, ws)

    except OSError as ose:
        print('Connection attempt failed: %s' % ose, file=stderr)


if __name__ == '__main__':
    trio.run(launch_bus)
