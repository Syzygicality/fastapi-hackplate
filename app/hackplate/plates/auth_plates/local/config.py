from app.hackplate.plates.abstract_plates import AuthPlate


class LocalPlate(AuthPlate):
    async def foobar(self) -> None:
        print("Hello world!")
