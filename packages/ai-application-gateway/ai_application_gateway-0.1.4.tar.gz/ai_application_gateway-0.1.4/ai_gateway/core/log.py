import json
import logging
import os
import re
import socket
import sys

from loguru import logger
from yarl import URL

from ai_gateway.config import config


def get_log_path():
    hostname = socket.gethostname()
    # If frozen, use the executable path
    if getattr(sys, "frozen", False):
        logdir = os.path.dirname(os.path.realpath(sys.executable))
    else:
        logdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return f"{logdir}/logs/{hostname}.log"



def check_and_replace_angle_brackets(string):
    return re.sub(r"<([^>]*)>", r"[\1]", string)


def url_serializer(obj):
    if isinstance(obj, URL):
        return str(obj)


def json_formatter(record: dict) -> str:
    # file = check_and_replace_angle_brackets(record["file"].name)
    function_name = check_and_replace_angle_brackets(record["function"])
    message = check_and_replace_angle_brackets(record["message"])
    message = message.replace("{", "{{").replace("}", "}}").replace("\n", " ")

    extra = ""
    if record["extra"]:
        extra = (
            check_and_replace_angle_brackets(
                json.dumps(record["extra"], default=url_serializer, ensure_ascii=False)
            )
            .replace("{", "{{")
            .replace("}", "}}")
        )
    formatting = (
        f'<green>{record["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}</green> | '
        + f'<level>{record["level"].name: <8}</level> | '
        + f'<cyan>{record["name"]}</cyan>:<cyan>{function_name}</cyan>:'
        + f'<cyan>{record["line"]}</cyan> | '
        + f"<level>{message}</level>"
    )
    if extra:
        formatting += f" | <level>{extra}</level>\n"
    else:
        formatting += "\n"

    if record["exception"]:
        formatting += "{exception}"
    return formatting


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6  # pylint: disable=protected-access

        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def init(log_path=get_log_path(), debug=config.debug):
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict  # pylint: disable=no-member
        if name.startswith("uvicorn.")
    )
    intercept_handler = InterceptHandler()
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []

    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(handlers=[intercept_handler], level=level, force=True)
    logging.getLogger("uvicorn.access").handlers = [intercept_handler]
    logging.getLogger("uvicorn").handlers = [intercept_handler]

    diagnose = bool(debug)

    handlers_config = [
        {
            "sink": sys.stdout,
            "level": level,
            "catch": True,
            "diagnose": diagnose,
            "backtrace": True,
            "serialize": False,
            "format": json_formatter,
        }
    ]

    if config.logging.enable_file:
        handlers_config.append(
            {
                "sink": log_path,
                "level": level,
                "serialize": False,
                "catch": True,
                "diagnose": diagnose,
                "backtrace": True,
                "enqueue": True,
                "rotation": "00:00",
                "retention": "30 days",
                # "compression": "tar.bz2",
                "format": json_formatter,
            }
        )

    logger.configure(**{"handlers": handlers_config})

    logging.getLogger("botocore").setLevel(logging.INFO)
