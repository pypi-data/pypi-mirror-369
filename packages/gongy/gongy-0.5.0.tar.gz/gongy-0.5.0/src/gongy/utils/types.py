"""Custom types."""

from __future__ import annotations

__all__: tuple[str, ...] = (
    "Milliseconds",
    "ms_to_timedelta",
    "timedelta_to_ms",
)

from datetime import timedelta
from typing import Annotated

from pydantic import BeforeValidator, PlainSerializer


def ms_to_timedelta(v: float | timedelta) -> timedelta:
    """Convert milliseconds to timedelta."""
    return timedelta(milliseconds=v) if isinstance(v, (int, float)) else v


def timedelta_to_ms(td: timedelta) -> int:
    """Convert timedelta to milliseconds."""
    return int(td.total_seconds() * 1000)


Milliseconds = Annotated[
    timedelta,
    BeforeValidator(ms_to_timedelta),
    PlainSerializer(timedelta_to_ms),
]
