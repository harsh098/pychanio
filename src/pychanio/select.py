# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Harsh Mishra

"""
select.py
=========

Implements a Go-style non-deterministic `select` block for awaiting multiple
channel operations concurrently.

Features:
---------
- Randomly selects among ready awaitables
- Supports handler functions for each case
- Optional `default` and `timeout` behaviors
- Cancels pending tasks after first completion

This is the concurrency control hub of pychanio, enabling expressive fan-in, fan-out,
and coordination patterns across multiple channels.
"""

import asyncio
import random
from typing import Any, Awaitable, Callable, Optional, Tuple


async def select(
    *cases: Tuple[Awaitable[Any], Callable[[Any, bool], Any]],
    default: Optional[Callable[[], Any]] = None,
    timeout: Optional[float] = None,
) -> Any:
    """
    Waits for the first of several awaitables to complete and dispatches its handler.

    Args:
        *cases: Tuples of (awaitable, handler), where handler receives (val, ok)
        default: Callable to run if no cases complete in time or all channels are empty.
        timeout: Max time (in seconds) to wait before default/timeout.

    Returns:
        Any: Result of the triggered handler.

    Raises:
        TimeoutError: If nothing completes and no default is given.
    """
    async def runner(coro, handler):
        val, ok = await coro
        return handler(val, ok)

    ready_cases = []
    empty_cases = []

    for coro, handler in cases:
        chan = getattr(coro, "__chan__", None)
        if chan and chan.empty():
            empty_cases.append((coro, handler))
        else:
            ready_cases.append((coro, handler))

    if not ready_cases:
        if default:
            return default()
        else:
            # fallback to using all cases (even if empty)
            ready_cases = empty_cases

    tasks = [asyncio.create_task(runner(coro, handler)) for coro, handler in ready_cases]

    done, pending = await asyncio.wait(
        tasks, timeout=timeout, return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()

    if not done:
        if default:
            return default()
        raise TimeoutError("select timed out")

    return await random.choice(list(done))

