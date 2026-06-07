from __future__ import annotations
from typing import TYPE_CHECKING, Any
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from app.hackplate.hackplate_types import Hackplate, HackplateRequest


class AuthPlate(ABC):
    @abstractmethod
    async def register_auth_routes(self, app: Hackplate) -> None: ...

    @abstractmethod
    async def authenticate(self, request: HackplateRequest) -> Any: ...


class DatabasePlate(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def ping(self) -> bool: ...

    @abstractmethod
    async def get_db(self): ...
