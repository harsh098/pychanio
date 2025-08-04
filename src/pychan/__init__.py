# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Harsh Mishra

"""
pychan
======

pychan brings Go-style concurrency to Python's asyncio world using channels and
select blocks.

This module re-exports the public API of the library, making it convenient to
import constructs like `chan`, `go`, `select`, and channel wrappers from a
single place.

Main Features:
--------------
- Full-duplex, send-only, and receive-only channels
- Buffered and unbuffered semantics
- Operator overloading (<<, >>) for DSL-like syntax
- Go-style goroutines via `go(...)`
- Non-deterministic select with timeout and default handling
- Nil channels that block forever
- Control-flow sentinels (e.g., DONE, CANCEL)

Example:
--------
```python
from pychan import chan, go, select, DONE

# Usage inside an async function
ch = chan()
go(lambda: ch << "hello")
msg, ok = await (ch >> None)
```
"""

from . import sentinels
from .core import Channel
from .interfaces import SendOnlyChannel, ReceiveOnlyChannel, split
from .dsl import ChannelDSL, chan, close
from .runners import go
from .nil import nil
from .select import select
from .exceptions import ChannelClosed

__all__ = [
    "Channel",
    "SendOnlyChannel",
    "ReceiveOnlyChannel",
    "ChannelDSL",
    "chan",
    "close",
    "split",
    "nil",
    "go",
    "select",
    "ChannelClosed",
    "sentinels",
]
