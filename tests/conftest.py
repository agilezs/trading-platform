import os


def get_http_url() -> str:
    host = os.getenv("FASTAPI_HTTP_HOST") or "http://localhost:8000"
    return host


def get_ws_url() -> str:
    host = os.getenv("FASTAPI_WS_HOST") or "ws://localhost:8000"
    return host
