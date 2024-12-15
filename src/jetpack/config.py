import os
import pathlib
from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class _LogConfig(BaseSettings):
    LOG_LEVEL: str = "INFO"
    ENABLE_FILE_LOG: Optional[bool] = False
    ENABLE_CONSOLE_LOG: Optional[bool] = True
    LOG_ENABLE_TRACEBACK: bool = Field(default=False)
    DEFER_LOG_MODULES = Optional[list] = ["httpx", "pymongo"]
    DEFER_ADDITIONAL_LOGS = Optional[list] = []
    DEFER_LOG_LEVEL: str = "INFO"


class _BasePathConf(BaseSettings):
    BASE_PATH: str = "code/data"


class _PathConf(BaseSettings):
    BASE_PATH: pathlib.Path = pathlib.Path(_BasePathConf().BASE_PATH)
    MODULE_NAME: str = Field("", validation_alias="MODULE_NAME")
    LOGS_MODULE_PATH: Optional[pathlib.Path]

    @model_validator(mode="before")
    def path_merger(cls, values):
        values["LOGS_MODULE_PATH"] = os.path.join(
            values.get("BASE_PATH"), "logs", values.get("MODULE_NAME").replace("-", "_")
        )
        return values


LogConfig = _LogConfig()
PathConf = _PathConf()

__all__ = ["LogConfig", "PathConf"]
