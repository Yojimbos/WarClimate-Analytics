from __future__ import annotations

import logging

from pythonjsonlogger.json import JsonFormatter


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d")
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
