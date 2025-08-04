# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Harsh Mishra

"""
nil.py
======

Defines the "nil" channel: a special channel that blocks forever on send/receive.

Nil channels mimic Go’s `nil` channels and are useful in `select()` blocks where
you may want to programmatically disable cases without conditionals.

Behavior:
---------
- Any send/receive on a nil channel will block indefinitely
- Used to disable select branches dynamically
"""

from .core import Channel


def nil() -> Channel:
    """
    Returns a nil channel that blocks on all operations.

    Returns:
        Channel: A nil channel instance.
    """
    return Channel(_is_nil=True)
