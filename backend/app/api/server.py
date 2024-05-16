import uuid
from json import JSONDecodeError

import uvicorn
from fastapi import FastAPI
from pydantic import ValidationError
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets import ConnectionClosed

from app.api.routes.orders import router as orders_router
from app.api.utils import random_delay, WsConnectionManager
from app.model.trading_platform_model import OrderOutput, OrderStatus, OrderInput, Error

app = FastAPI(title="Forex Trading Platform API")

app.include_router(orders_router, prefix="/orders")

ws_manager = WsConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_json()
                input_model = OrderInput(**data)
                order_id = str(uuid.uuid4())
                for order_status in [OrderStatus.pending, OrderStatus.executed, OrderStatus.cancelled]:
                    await random_delay()
                    await ws_manager.broadcast(OrderOutput(id=order_id,
                                                           stocks=input_model.stocks,
                                                           quantity=input_model.quantity,
                                                           status=order_status)
                                               .model_dump(exclude_none=True))

            except (ValidationError, JSONDecodeError) as e:
                # send error to the client so they know what happened
                await websocket.send_json({"error": "Validation error",
                                           **Error(code=status.WS_1003_UNSUPPORTED_DATA,
                                                   message=str(e))
                                          .model_dump(exclude_none=True)})

    except (WebSocketDisconnect, ConnectionClosed):
        # handle disconnection gracefully
        ws_manager.disconnect(websocket)
    except Exception as e:
        await websocket.send_json({"error": str(e)})


if __name__ == '__main__':
    uvicorn.run("backend.app.api.server:app", reload=False)
