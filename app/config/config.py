from fastapi import FastAPI, Request
from starlette.datastructures import State

from app.db.sqlite.config import SQLitePlate
from app.db.abstract_plate import DatabasePlate


class BackendConfig:
    def __init__(self):
        self.db: DatabasePlate = SQLitePlate()
        self.auth = None


class AppState(State):
    config: BackendConfig


class Hackplate(FastAPI):
    state: AppState


class HackplateRequest(Request):
    app: Hackplate
