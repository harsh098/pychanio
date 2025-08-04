# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Harsh Mishra

"""
dsl.py
======

Provides operator overloading for channels to enable DSL-style syntax.

Extends the base `Channel` to define:
- `ch << value` for asynchronous send
- `await (ch >> None)` for asynchronous receive
- `async for x in ch` for iteration over messages

This is the primary user-facing interface for sending and receiving values in a
Go-like fashion.
"""

import asyncio
from typing import Any
from .core import Channel
from .exceptions import ChannelClosed


class ChannelDSL(Channel):
    """
    Extension of Channel that supports operator DSLs:

        ch << value     # send
        await (ch >> _) # receive
        async for x in ch: ...

    Raises:
        ChannelClosed: On send or receive after closure.
    """

    def __lshift__(self, item: Any):
        if self._is_nil:
            return asyncio.Future()
        if self._closed:
            raise ChannelClosed("Send on closed channel")
        return asyncio.create_task(self._queue.put(item))
    
    async def send(self, item):
        if self._is_nil:
            await asyncio.Future()
        if self._closed:
            raise ChannelClosed("send on closed channel")
        await self._queue.put(item)
    
    def receive(self):
        async def _recv_coro() -> tuple[Any, bool]:
            if self._is_nil:
                await asyncio.Future()
            if self._closed and self._queue.empty():
                return None, False
            ok = not self._closed
            val = await self._queue.get()
            return val, ok 
        
        _recv_coro.__chan__ = self._queue

        return _recv_coro()


    def __rshift__(self, _: Any):
        return self.receive()

    def __aiter__(self):
        return self

    async def __anext__(self):
        val, ok = await (self >> None)
        if not ok:
            raise StopAsyncIteration
        return val


def chan(capacity: int = 0) -> ChannelDSL:
    """
    Creates a new full-duplex channel.

    Args:
        capacity (int): Size of internal buffer. 0 for unbuffered.

    Returns:
        ChannelDSL: A new channel instance.
    """
    return ChannelDSL(capacity)


def close(ch: ChannelDSL) -> None:
    """
    Closes a given channel.

    Args:
        ch (ChannelDSL): The channel to close.
    """
    ch.close()
