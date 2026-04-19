from typing import Any

from pydantic_settings import (
    BaseSettings,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)


class TOMLSettings(BaseSettings):
    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("tool", "hackplate"),
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        **kwargs: Any,
    ) -> tuple[PyprojectTomlConfigSettingsSource]:
        return (PyprojectTomlConfigSettingsSource(settings_cls),)


class ProjectDetails(TOMLSettings):
    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("project",),
        extra="ignore",
    )

    name: str = "fastapi-hackplate"
    version: str = "0.1.0"
    description: str = ""


# --- Usage Example ---
# Define fields in pyproject.toml under [tool.hackplate]:
#
#   [tool.hackplate]
#   app_title = "My App"
#   debug = true
#
# Subclass TOMLSettings and declare matching fields:
#
#   class MySettings(TOMLSettings):
#       app_title: str = "fastapi-hackplate"
#       debug: bool = False
#
#   settings = MySettings()
#   print(settings.app_title)  # "My App"
