import json
import logging
import sys

import structlog

from app.config import get_config

config = get_config()


def write_to_file(file_path, event_dict):
    """Write the log entry to a file."""
    if event_dict.get("analytics", False):
        file_path = config.ANALYTICS_LOG_FILE
    else:
        file_path = config.LOG_FILE

    with open(file_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(event_dict, default=str) + "\n")
    return event_dict


def setup_logging():
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
    ]

    if sys.stdout.isatty():
        output_processors = [structlog.dev.ConsoleRenderer(colors=True)]
    else:
        output_processors = [
            lambda logger, name, event_dict: write_to_file(config.LOG_FILE, event_dict),
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=shared_processors + output_processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
