import trio
from trio_websocket import ConnectionClosed, serve_websocket


async def serve(request):
    ws = await request.accept()
    while True:
        try:
            message = await ws.get_message()
            print(message)
        except ConnectionClosed:
            break


async def main():
    await serve_websocket(serve, '127.0.0.1', 8080, ssl_context=None)


if __name__ == '__main__':
    trio.run(main)
