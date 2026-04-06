from app.hackplate.types import Hackplate
from app.lifespan import lifespan
from app.hackplate.exceptions import register_exception_handlers

app = Hackplate(lifespan=lifespan)
register_exception_handlers(app)
