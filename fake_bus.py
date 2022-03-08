import json
from sys import stderr

import trio
from trio_websocket import open_websocket_url

ROUTES = 'routes/156.json'
TIMEOUT = 1


def extract_routes(filename):
    with open(filename, 'r') as file:
        return json.load(file)


async def launch_bus():
    routes = extract_routes(ROUTES)
    message = {
        'msgType': 'Buses',
        'buses': [
            {
                'busId': f'{routes["name"]}-0',
                'route': routes['name'],
            },
        ],
    }

    try:
        async with open_websocket_url('ws://127.0.0.1:8080') as ws:
            for coordinates in routes['coordinates']:
                message['buses'][0].update(
                    {'lat': coordinates[0], 'lng': coordinates[1]}
                )
                await ws.send_message(json.dumps(message))
                await trio.sleep(TIMEOUT)

    except OSError as ose:
        print('Connection attempt failed: %s' % ose, file=stderr)


if __name__ == '__main__':
    trio.run(launch_bus)
