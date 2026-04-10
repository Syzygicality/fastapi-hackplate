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


class HackplateRequest(Request):
    """
    Custom class to to bind BackendConfig to request objects. Use in place of type and class `Request`
    """

    app: Hackplate
