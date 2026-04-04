from app.config.config import Hackplate
from app.lifespan import lifespan

app = Hackplate(lifespan=lifespan)
