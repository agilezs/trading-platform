import asyncio
import json
import random
import statistics
import time
from dataclasses import dataclass

import websockets
from httpx import AsyncClient
from loguru import logger
from starlette import status

from tests.conftest import get_http_url, get_ws_url


@dataclass
class Duration:
    start_time = time.time()
    end_time = None


placed_orders = []
order_times = {}


async def create_order(client: AsyncClient):
    duration = Duration()
    response = await client.post("/orders", json={"stocks": "EURUSD",
                                                  "quantity": random.uniform(0.5, 1000000.0)})
    if response.status_code == status.HTTP_201_CREATED:
        order_id = response.json().get("id")
        logger.info(f"Order created with id '{order_id}'")
        placed_orders.append(order_id)
        order_times[order_id] = duration
    logger.info(f"Failed to place order: {response.json()}")


async def receive_ws_messages():
    async with websockets.connect(get_ws_url() + "/ws") as websocket_client:
        counter = 0
        while True:
            message = json.loads(await websocket_client.recv())
            order_id = message.get("id")
            if message.get("status") == "executed":
                counter += 1
                logger.info(f"Received message with id '{order_id}' and count is '{counter}'")
                order_times[order_id].end_time = time.time()
                placed_orders.remove(message.get("id"))
            if len(placed_orders) == 0:
                break


async def main():
    async with AsyncClient(base_url=get_http_url(), follow_redirects=True) as client:
        tasks = [asyncio.create_task(receive_ws_messages())]
        tasks.extend([asyncio.create_task(create_order(client)) for _ in range(100)])
        await asyncio.gather(*tasks)

    execution_delays = [duration.end_time - duration.start_time for order_id, duration in order_times.items()]
    average_delay = statistics.mean(execution_delays)
    standard_deviation_delay = statistics.stdev(execution_delays)
    logger.info(f"Average order execution delay: {average_delay:.2f} seconds")
    logger.info(f"Standard deviation of order execution delay: {standard_deviation_delay:.2f} seconds")
    logger.info(f"Total orders processed: {len(order_times)}")

    for order_id, duration in order_times.items():
        logger.info(f"Order '{order_id}' Duration: {duration.end_time - duration.start_time:.2f}")


if __name__ == '__main__':
    asyncio.run(main())
