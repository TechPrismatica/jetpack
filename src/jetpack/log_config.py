import logging
import pathlib
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from jetpack.config import LogConfig, PathConf


def read_configuration(project_name: str):
    return {
        "name": project_name,
        "handlers": [
            {
                "type": "RotatingFileHandler",
                "max_bytes": 100000000,
                "back_up_count": 5,
                "enable": LogConfig.ENABLE_FILE_LOG,
            },
            {"type": "StreamHandler", "enable": LogConfig.ENABLE_CONSOLE_LOG},
        ],
    }


def configure_logger(project_name: str = PathConf.MODULE_NAME):
    """
    Creates a rotating log
    """
    logging_config = read_configuration(project_name=project_name)
    __logger__ = logging.getLogger()
    __logger__.setLevel(LogConfig.LOG_LEVEL)
    __logger__.handlers = []
    for each_module in LogConfig.DEFER_LOG_MODULES:
        logging.getLogger(each_module).setLevel(LogConfig.DEFER_LOG_LEVEL)
    for each_module in LogConfig.DEFER_ADDITIONAL_LOGS:
        logging.getLogger(each_module).setLevel(LogConfig.DEFER_LOG_LEVEL)
    log_formatter = "%(asctime)s - %(levelname)-6s - [%(threadName)5s:%(funcName)5s(): %(lineno)s] - %(message)s"
    time_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_formatter, time_format)
    for each_handler in logging_config["handlers"]:
        if each_handler["type"] in ["RotatingFileHandler"] and each_handler.get(
            "enable", False
        ):
            PathConf.LOGS_MODULE_PATH.mkdir(parents=True, exist_ok=True)
            log_file = pathlib.Path(PathConf.LOGS_MODULE_PATH, f"{project_name}.log")
            temp_handler = RotatingFileHandler(
                log_file,
                maxBytes=each_handler["max_bytes"],
                backupCount=each_handler["back_up_count"],
            )
            temp_handler.setFormatter(formatter)
        elif each_handler["type"] in ["StreamHandler"] and each_handler.get(
            "enable", True
        ):
            temp_handler = StreamHandler()
            temp_handler.setFormatter(formatter)
        else:
            continue
        __logger__.addHandler(temp_handler)
    return __logger__
