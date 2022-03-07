from sys import stderr

import trio
from trio_websocket import open_websocket_url


async def main():
    try:
        async with open_websocket_url('wss://echo.websocket.org') as ws:
            await ws.send_message('hello world!')
            message = await ws.get_message()
            print('Received message: %s' % message)
    except OSError as ose:
        print('Connection attempt failed: %s' % ose, file=stderr)


if __name__ == '__main__':
    trio.run(main)
