from abc import ABC, abstractmethod


class AuthPlate(ABC):
    @abstractmethod
    async def foobar(self) -> None: ...
