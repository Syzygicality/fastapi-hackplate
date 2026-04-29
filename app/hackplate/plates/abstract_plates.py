from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from collections.abc import Callable

if TYPE_CHECKING:
    from app.hackplate.hackplate_types import Hackplate


class AuthPlate(ABC):
    @abstractmethod
    async def register_auth_routes(self, app: Hackplate) -> None: ...

    @abstractmethod
    def get_current_user(self) -> Callable: ...


class DatabasePlate(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def ping(self) -> bool: ...

    @abstractmethod
    async def get_db(self): ...
