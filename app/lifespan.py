from contextlib import contextmanager
from fastapi import FastAPI
from collections.abc import Generator


@contextmanager
def lifespan(_: FastAPI) -> Generator[None, None]:
    yield
