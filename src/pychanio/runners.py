# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Harsh Mishra

"""
runners.py
==========

Provides goroutine-style utilities for launching coroutines in the background.

`go()` is the core function that schedules an awaitable using `asyncio.create_task`
to simulate Go's `go f(...)` syntax.

Intended for ergonomic spawning of concurrent tasks in fire-and-forget style.
"""

import asyncio
from typing import Any, Callable, Awaitable


def go(func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> asyncio.Task:
    """
    Starts a coroutine as a background task, similar to Go's goroutines.

    Args:
        func: Coroutine function to run.
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        asyncio.Task: Running task.
    """
    return asyncio.create_task(func(*args, **kwargs))
