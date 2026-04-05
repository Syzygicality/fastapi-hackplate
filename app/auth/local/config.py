from app.auth.abstract_plate import AuthPlate


class LocalPlate(AuthPlate):
    async def foobar(self) -> None:
        print("Hello world!")
