from app.types import Hackplate
from app.lifespan import lifespan

app = Hackplate(lifespan=lifespan)
