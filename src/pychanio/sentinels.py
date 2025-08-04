# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Harsh Mishra

"""
sentinels.py
============

Defines reusable singleton control messages (sentinels) to enable structured
control flow over channels.

Sentinels help communicate semantic meaning such as:
- `DONE`: Indicates shutdown
- `CANCEL`: Cancels in-progress operations
- `HEARTBEAT`: Keep-alive or ping messages

These values are identity-comparable and printable. You can also define your own.

Sentinels are useful in:
- Fan-in consumers
- Graceful shutdown logic
- Complex pipelines needing out-of-band control
"""


__all__ = ["Sentinel", "DONE", "CANCEL", "HEARTBEAT", "is_signal"]


class Sentinel:
    """
    A singleton signal object used to represent a special message in channels.

    Instances of this class are comparable by identity, and printable by name.

    Parameters
    ----------
    name : str
        A human-readable identifier for the sentinel (e.g., "DONE").

    Examples
    --------
    >>> DONE = Sentinel("DONE")
    >>> msg = DONE
    >>> if msg is DONE:
    ...     handle_shutdown()
    """
    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"<Signal: {self.name}>"

    def __str__(self) -> str:
        return self.name


#: Sentinel indicating shutdown or completion.
DONE = Sentinel("DONE")

#: Sentinel indicating operation cancellation.
CANCEL = Sentinel("CANCEL")

#: Sentinel for heartbeat/liveness signals.
HEARTBEAT = Sentinel("HEARTBEAT")


def is_signal(obj) -> bool:
    """
    Check if the given object is a Sentinel instance.

    This is useful when processing messages from channels that may contain
    both data and control signals.

    This function allows users to perform:

    1. Pattern matching across multiple signals
    2. Unified signal handling without hard-coding signal names
    3. Clear separation of data and control messages in channel flows
    4. Filtering logic in pipelines based on whether values are signal types

    Parameters
    ----------
    obj : Any
        The object to inspect.

    Returns
    -------
    bool
        True if the object is a Sentinel, False otherwise.

    Examples
    --------
    >>> is_signal(DONE)
    True
    >>> is_signal("data")
    False

    Typical Usage
    -------------
    >>> async for msg in ch:
    ...     if is_signal(msg):
    ...         handle_signal(msg)
    ...     else:
    ...         process_data(msg)
    """
    return isinstance(obj, Sentinel)
