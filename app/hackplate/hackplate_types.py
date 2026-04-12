from fastapi import FastAPI, Request
from starlette.datastructures import State

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

    def __init__(self, **kwargs):
        from app.hackplate.lifespan import hackplate_lifespan

        kwargs.setdefault("lifespan", hackplate_lifespan)
        super().__init__(**kwargs)


class HackplateRequest(Request):
    """
    Custom class to to bind BackendConfig to request objects. Use in place of type and class `Request`
    """

    app: Hackplate
