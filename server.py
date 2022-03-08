import json

import trio
from trio_websocket import ConnectionClosed, serve_websocket

ROUTES = 'routes/156.json'
TIMEOUT = 0.5


def extract_routes(filename):
    with open(filename, 'r') as file:
        return json.load(file)


async def launch_buses(request):
    routes = extract_routes(ROUTES)

    message = {
        "msgType": "Buses",
        "buses": [
            {
                "busId": "c790сс",
                "route": routes['name'],
            },
        ],
    }

    ws = await request.accept()
    for coordinates in routes['coordinates']:
        try:
            message['buses'][0].update(
                {'lat': coordinates[0], 'lng': coordinates[1]}
            )
            await ws.send_message(json.dumps(message))
            await trio.sleep(TIMEOUT)
        except ConnectionClosed:
            break


async def main():
    await serve_websocket(launch_buses, '127.0.0.1', 8000, ssl_context=None)


if __name__ == '__main__':
    trio.run(main)
