from __future__ import annotations
from typing import Callable

from shortuuid import uuid as shortuuid


def generator(prefix: str = "") -> Callable:
    """Generate a short UUID"""

    def gen() -> str:
        if prefix:
            return f"{prefix}-{shortuuid()}"
        return shortuuid()

    return gen


def uuid(prefix: str = "", name: str | None = None) -> str:
    if prefix:
        return f"{prefix}-{shortuuid(name)}"
    return shortuuid(name)


