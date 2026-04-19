from app.hackplate.hackplate_types import Hackplate
from app.hackplate.lifespan import configure
from app.lifespan import lifespan, pre_hackplate_lifespan


def register_routes(app: Hackplate) -> None:
    """
    Function for registering routers.

    Args:
        app: initialized Hackplate object originating from main.py
    """
    pass


app = Hackplate(
    title="FastAPI Hackplate",
    description="A FastAPI hackathon boilerplate for rapid development and deployment.",
    version="0.1.0",
    pre_hackplate_lifespan=pre_hackplate_lifespan,
    post_hackplate_lifespan=lifespan,
)

configure(
    app,
    [
        register_routes,
    ],
)
