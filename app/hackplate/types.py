from fastapi import FastAPI, Request
from starlette.datastructures import State

from app.hackplate.config import BackendConfig


class AppState(State):
    config: BackendConfig


class Hackplate(FastAPI):
    state: AppState


class HackplateRequest(Request):
    app: Hackplate
