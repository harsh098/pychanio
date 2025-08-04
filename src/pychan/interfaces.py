# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Harsh Mishra

"""
interfaces.py
=============

Implements send-only and receive-only wrappers for channels.

The `split()` utility function returns `SendOnlyChannel` and `ReceiveOnlyChannel`
interfaces to enforce separation of responsibilities and provide type safety
in channel usage.

Useful when you want to expose a channel to other tasks while restricting their
capabilities (e.g., producers shouldn't receive).
"""


from typing import Any
from .core import Channel


class SendOnlyChannel:
    """
    A wrapper that exposes only the send (`<<`) operation of a channel.

    Args:
        ch (Channel): A full-duplex channel to wrap.
    """

    def __init__(self, ch: Channel):
        self.ch = ch

    def close(self):
        self.ch.close()

    def __lshift__(self, item: Any):
        """
        Sends an item to the channel.

        Args:
            item (Any): Item to send.

        Returns:
            asyncio.Task: The sending task.
        """
        return self.ch << item


class ReceiveOnlyChannel:
    """
    A wrapper that exposes only the receive (`>>`) operation of a channel.

    Args:
        ch (Channel): A full-duplex channel to wrap.
    """

    def __init__(self, ch: Channel):
        self.ch = ch

    def __rshift__(self, _: Any):
        """
        Receives an item from the channel.

        Returns:
            Awaitable: An awaitable receiving future.
        """
        return self.ch >> None

    def close(self):
        self.ch.close()

    def __aiter__(self):
        return self.ch.__aiter__()

    async def __anext__(self):
        return await self.ch.__anext__()


def split(ch: Channel) -> tuple[SendOnlyChannel, ReceiveOnlyChannel]:
    """
    Splits a full channel into send-only and receive-only views.

    Args:
        ch (Channel): The channel to split.

    Returns:
        tuple: (SendOnlyChannel, ReceiveOnlyChannel)
    """
    return SendOnlyChannel(ch), ReceiveOnlyChannel(ch)
