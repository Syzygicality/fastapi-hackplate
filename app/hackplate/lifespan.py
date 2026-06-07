from contextlib import asynccontextmanager, AsyncExitStack
from collections.abc import AsyncGenerator, Callable

from app.hackplate.config import BackendConfig
from app.hackplate.cors import register_cors_middleware
from app.hackplate.exceptions import register_exception_handlers
from app.hackplate.logging import setup_logging
from app.hackplate.hackplate_types import Hackplate
from app.hackplate.toml_settings import BackendTOMLSettings


@asynccontextmanager
async def hackplate_base_lifespan(app: Hackplate) -> AsyncGenerator[None, None]:
    settings = BackendTOMLSettings()
    app.state.settings = settings
    config = BackendConfig(settings)
    app.state.config = config
    yield


@asynccontextmanager
async def hackplate_config_lifespan(app: Hackplate) -> AsyncGenerator[None, None]:
    setup_logging()
    await app.state.config.auth.register_auth_routes(app)
    await app.state.config.db.connect()
    yield
    await app.state.config.db.disconnect()


@asynccontextmanager
async def hackplate_lifespan(app: Hackplate) -> AsyncGenerator[None, None]:
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(hackplate_base_lifespan(app))
        if app.pre_hackplate_lifespan:
            await stack.enter_async_context(app.pre_hackplate_lifespan(app))
        await stack.enter_async_context(hackplate_config_lifespan(app))
        if app.post_hackplate_lifespan:
            await stack.enter_async_context(app.post_hackplate_lifespan(app))
        yield


def configure(app: Hackplate, register_functions: Callable[[Hackplate], None]):
    """
    Centralizes app configuration logic

    Args:
        app: initialized Hackplate object originating from main.py
        register_functions: list of functions with a single `app: Hackplate` param
    """
    register_exception_handlers(app)
    register_cors_middleware(app)

    for fn in register_functions:
        try:
            fn(app)
        except Exception as e:
            raise RuntimeError(f"Failed to register {fn.__name__}") from e
