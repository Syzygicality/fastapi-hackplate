from fastapi import FastAPI, Request, WebSocket
from starlette.datastructures import State
from typing import Callable, AsyncContextManager

from app.hackplate.config import BackendConfig


class _AppState(State):
    """
    Intermediary class to bind BackendConfig to the state
    """

    config: BackendConfig


class Hackplate(FastAPI):
    """
    Custom class to to bind BackendConfig to the app object. Use in place of type and class `FastAPI`
    """

    state: _AppState
    pre_lifespan: Callable[["Hackplate"], AsyncContextManager] | None = None
    post_lifespan: Callable[["Hackplate"], AsyncContextManager] | None = None

    def __init__(
        self, pre_hackplate_lifespan=None, post_hackplate_lifespan=None, **kwargs
    ):
        from app.hackplate.lifespan import hackplate_lifespan

        kwargs.setdefault("lifespan", hackplate_lifespan)
        super().__init__(**kwargs)

        self.pre_lifespan = pre_hackplate_lifespan
        self.post_lifespan = post_hackplate_lifespan


class HackplateRequest(Request):
    """
    Custom class to to bind BackendConfig to request objects. Use in place of type and class `Request`
    """

    app: Hackplate


class HackplateWebSocket(WebSocket):
    """
    Custom class to to bind BackendConfig to websocket objects. Use in place of type and class `WebSocket`
    """

    app: Hackplate
