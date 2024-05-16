from asyncio import sleep
from random import uniform

from starlette.websockets import WebSocket


async def random_delay():
    # delay between 0.1 and 1 second
    delay = uniform(0.1, 1)
    await sleep(delay=delay)


class WsConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        for connection in self.active_connections:
            await connection.send_json(message)
