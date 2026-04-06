from abc import ABC, abstractmethod


class AuthPlate(ABC):
    @abstractmethod
    async def foobar(self) -> None: ...


class DatabasePlate(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def ping(self) -> bool: ...

    @abstractmethod
    async def get_session(self): ...
