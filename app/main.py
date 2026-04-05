from app.types import Hackplate
from app.lifespan import lifespan
from app.config.exceptions import register_exception_handlers

app = Hackplate(lifespan=lifespan)
register_exception_handlers(app)
