from asyncio import sleep
from random import uniform

from app.api.websocket_manager import WebSocketManager
from app.model.trading_platform_model import OrderOutput, OrderStatus, OrderInput

orders_db = {}


async def random_delay():
    # delay between 0.1 and 1 second
    delay = uniform(0.1, 1)
    await sleep(delay=delay)


async def update_order_status(order_id: str, input_model: OrderInput, ws_manager: WebSocketManager):
    order = orders_db.get(order_id)
    for order_status in [OrderStatus.pending, OrderStatus.executed, OrderStatus.cancelled]:
        await random_delay()
        order.status = order_status.value
        await ws_manager.broadcast(OrderOutput(id=order_id,
                                               stocks=input_model.stocks,
                                               quantity=input_model.quantity,
                                               status=order_status)
                                   .model_dump(exclude_none=True))
