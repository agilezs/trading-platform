import uuid
from json import JSONDecodeError

from fastapi import APIRouter
from pydantic import ValidationError
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets import ConnectionClosed

from app.api.utils import orders_db, random_delay
from app.api.websocket_manager import ws_manager
from app.model.trading_platform_model import OrderInput, OrderOutput, OrderStatus, Error

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_json()
                input_model = OrderInput(**data)
                order_id = str(uuid.uuid4())
                orders_db[order_id] = OrderOutput.construct(id=order_id,
                                                            stocks=input_model.stocks,
                                                            quantity=input_model.quantity)
                for order_status in [OrderStatus.pending, OrderStatus.executed, OrderStatus.cancelled]:
                    await random_delay()
                    order = orders_db[order_id]
                    order.status = order_status.value
                    await ws_manager.broadcast(order.model_dump(exclude_none=True))

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
