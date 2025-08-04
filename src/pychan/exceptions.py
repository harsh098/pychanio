# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Harsh Mishra

"""
exceptions.py
=============

Defines custom exception classes used by pychan.

Currently includes:
- `ChannelClosed`: Raised when attempting to send to or receive from a closed channel.

These exceptions help enforce safe communication patterns and allow users to
gracefully handle edge cases in concurrent flows.
"""


class ChannelClosed(Exception):
    """
    Raised when sending to or receiving from a closed channel.
    """

    pass
