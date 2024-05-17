import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes.orders import router as orders_router
from app.api.routes.websockets import router as websocket_router
from app.model.trading_platform_model import RequestError

app = FastAPI(title="Forex Trading Platform API")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [RequestError(message=error.get("msg"),
                           input=error.get("input"),
                           localization=error.get("loc"),
                           type=error.get("type")).model_dump(exclude_none=True, exclude_defaults=True,
                                                              exclude_unset=True) for error in exc.errors()]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"errors": errors})
    )


app.include_router(orders_router, prefix="/orders")
app.include_router(websocket_router)


if __name__ == '__main__':
    uvicorn.run("backend.app.server:app", reload=False)
