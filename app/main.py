from app.hackplate.types import Hackplate
from app.hackplate.lifespan import hackplate_lifespan
from app.hackplate.exceptions import register_exception_handlers


def register_routes(app: Hackplate) -> None:
    pass


app = Hackplate(lifespan=hackplate_lifespan)


register_routes(app)
register_exception_handlers(app)
