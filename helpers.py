import functools
import json
import logging
import os

import trio
from trio_websocket import ConnectionClosed, HandshakeError

logger = logging.getLogger(__name__)

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
