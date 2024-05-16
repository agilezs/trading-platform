import uuid
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException
from starlette import status

from app.api.utils import random_delay
from app.model.trading_platform_model import OrderOutput, OrderInput, OrderStatus, Error

router = APIRouter()

database = {}


@router.get(
    "/",
    response_model=list[OrderOutput],
    name="orders:getOrders"
)
async def get_orders(
        # orders: Annotated[list[OrderOutput], Depends(list_orders)]
) -> list[OrderOutput]:
    await random_delay()
    return [v for v in database.values()]


@router.post(
    "/",
    response_model=OrderOutput,
    response_model_exclude_none=True,
    name="orders:placeOrder",
    status_code=status.HTTP_201_CREATED,
)
async def place_order(order: Annotated[OrderInput, Body]) -> OrderOutput:
    order_output = OrderOutput(
        id=str(uuid.uuid4()),
        stocks=order.stocks,
        quantity=order.quantity,
        status=OrderStatus.pending)
    await random_delay()
    database[order_output.id] = order_output
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
    order = database.get(order_id)
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
    if order := database.get(order_id):
        database.pop(order.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found!"
        )
