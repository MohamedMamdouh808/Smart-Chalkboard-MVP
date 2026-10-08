"""Background workers — heavy work off the UI thread."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from typing import TypeVar

T = TypeVar("T")

_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="smartboard")


def submit(fn: Callable[..., T], *args: object, **kwargs: object) -> Future[T]:
    return _pool.submit(fn, *args, **kwargs)
