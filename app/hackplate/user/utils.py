import importlib
from functools import lru_cache

from app.hackplate.toml_settings import GeneralSettings
from app.hackplate.user.models import AbstractUser, AbstractUserDocument


@lru_cache(maxsize=1)
def get_user_model() -> type[AbstractUser] | type[AbstractUserDocument]:
    settings = GeneralSettings()
    module_path, class_name = settings.auth_user_model.rsplit(".", 1)
    module = importlib.import_module(module_path)
    model = getattr(module, class_name)
    if not issubclass(model, (AbstractUser, AbstractUserDocument)):
        raise ValueError(
            f"{settings.auth_user_model} must inherit from AbstractUser or AbstractUserDocument"
        )
    return model
