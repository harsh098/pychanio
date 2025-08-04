# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Harsh Mishra

"""
core.py
=======

Implements the fundamental `Channel` class used throughout pychanio.

Channels act as coroutine-safe message queues with optional buffering, closure
semantics, and support for blocking operations.

Key Features:
-------------
- Unbuffered or buffered channels
- Graceful closure detection
- Internal use of asyncio.Queue
- Basis for higher-level abstractions like `ChannelDSL` and select blocks
"""

from asyncio import Queue
from typing import Any


class Channel:
    """
    Represents a full-duplex coroutine-safe communication channel.

    Args:
        capacity (int): Maximum number of buffered items. Defaults to 0 (unbuffered).
        _is_nil (bool): If True, the channel blocks forever on send/receive.

    Attributes:
        capacity (int): Channel buffer size.
        _queue (asyncio.Queue): Internal asyncio queue.
        _closed (bool): Indicates if the channel is closed.
        _is_nil (bool): Indicates if the channel is a nil channel.
    """

    def __init__(self, capacity: int = 0, _is_nil: bool = False) -> None:
        self.capacity = capacity
        self._queue: Queue[Any] = Queue(maxsize=capacity)
        self._closed: bool = False
        self._is_nil: bool = _is_nil
        if capacity < 0:
            raise ValueError("Channel capacity must be non-negative")

    @property
    def closed(self):
        return self._closed

    def close(self) -> None:
        """
        Closes the channel. Further sends will raise ChannelClosed.
        """
        self._closed = True
