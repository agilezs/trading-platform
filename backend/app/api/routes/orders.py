import uuid

from fastapi import APIRouter, HTTPException, BackgroundTasks
from starlette import status

from app.api.websocket_manager import ws_manager
from app.api.utils import random_delay, orders_db, update_order_status
from app.model.trading_platform_model import OrderOutput, OrderInput, OrderStatus

router = APIRouter()


@router.get(
    "/",
    response_model=list[OrderOutput],
    name="orders:getOrders"
)
async def get_orders(
        # orders: Annotated[list[OrderOutput], Depends(list_orders)]
) -> list[OrderOutput]:
    await random_delay()
    return [v for v in orders_db.values()]


@router.post(
    "/",
    response_model=OrderOutput,
    response_model_exclude_none=True,
    name="orders:placeOrder",
    status_code=status.HTTP_201_CREATED,
)
async def place_order(order: OrderInput,
                      background_tasks: BackgroundTasks) -> OrderOutput:
    order_output = OrderOutput(
        id=str(uuid.uuid4()),
        stocks=order.stocks,
        quantity=order.quantity,
        status=OrderStatus.pending)
    await random_delay()
    orders_db[order_output.id] = order_output
    background_tasks.add_task(update_order_status, order_output.id, order, ws_manager)
    return order_output


@router.get(
    "/{order_id}",
    response_model=OrderOutput,
    response_model_exclude_none=True,
    name="orders:getOrder",
    status_code=status.HTTP_200_OK,
)
async def get_order_by_id(order_id: str) -> OrderOutput:
    await random_delay()
    order = orders_db.get(order_id)
    if order:
        return order
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Order not found!")


@router.delete(
    "/{order_id}",
    name="orders:cancelOrder",
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_order(order_id: str) -> None:
    await random_delay()
    if order := orders_db.get(order_id):
        orders_db.pop(order.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found!"
        )
