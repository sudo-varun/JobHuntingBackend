"""Logging configuration for the job hunting app.

Outputs structured logs to stdout so they appear in the uvicorn process
output (and in pod logs when running on Kubernetes / any container runtime).

Usage:
    from job_hunting.logging_config import setup_logging
    setup_logging()

Log levels can be controlled via the LOG_LEVEL environment variable
(default: INFO).  Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL.
"""
from __future__ import annotations

import logging
import logging.config
import os


def setup_logging() -> None:
    """Configure root and app-level loggers to write to stdout."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["stdout"],
        },
        # keep uvicorn's own loggers but route them through our handler
        "loggers": {
            "uvicorn": {"handlers": ["stdout"], "level": log_level, "propagate": False},
            "uvicorn.error": {"handlers": ["stdout"], "level": log_level, "propagate": False},
            "uvicorn.access": {"handlers": ["stdout"], "level": log_level, "propagate": False},
            "job_hunting": {"handlers": ["stdout"], "level": log_level, "propagate": False},
        },
    }

    logging.config.dictConfig(logging_config)

