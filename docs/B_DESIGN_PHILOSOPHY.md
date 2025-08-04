# Design Philosophy of pychanio

pychanio is a concurrency library that aims to bring Go-style channel-based programming and non-deterministic `select` semantics to Python's `asyncio` ecosystem. The design philosophy behind pychanio is guided by two primary goals:

1. **Provide Go-like concurrency semantics.**
2. **Preserve idiomatic Python style and ecosystem compatibility.**

This document outlines how these goals have been achieved, the trade-offs involved, and the core principles that shape pychanio.

---

## Goal 1: Provide Go-like Semantics

### Channels

* **First-class Channel types** (`Channel`, `SendChannel`, `RecvChannel`) mirror Go's communication primitives.
* Supports **buffered and unbuffered channels** with FIFO behavior.
* DSL support for `ch << val` (send) and `await (ch >> None)` (recv) offers syntax resembling Go.
* `async for x in ch:` allows idiomatic iteration over a channel.

### Select Blocks

* Inspired directly by Go's `select {}` construct.
* pychanio provides a `select()` function which accepts multiple awaitable cases with handlers, an optional `default`, and a `timeout`.
* Execution is **non-deterministic**, enabling realistic race behavior across multiple channels.

### Goroutines

* Python’s `asyncio.create_task()` is wrapped using a simple `go(...)` utility function to emulate Go's `go func()`.
* Tasks returned are cancellable and awaitable, consistent with Python idioms.

### Nil Channels

* Nil channels (`NilChannel`) are explicitly non-operational and useful for dynamically disabling branches inside select blocks.

### Sentinels

* Built-in singleton values like `DONE`, `CANCEL`, `HEARTBEAT` allow users to build coordination logic.
* `is_signal()` pattern enables readable branching logic.
* Promotes data/control separation, similar to Go’s idiomatic use of `close(chan)` and `nil`.

### Partial Blocking Semantics

* Buffered channels behave as expected.
* Unbuffered channels currently lack Go’s blocking semantics but this trade-off is explicitly documented.
* Future plans to improve this include backpressure simulation and two-party handshakes.

---

## Goal 2: Preserve Idiomatic Python Style

### No Framework, Just `asyncio`

* pychanio is a library, not a framework. There is no runtime, lifecycle manager, or event loop replacement.
* Integrates seamlessly into existing asyncio applications and third-party libraries.

### DSL That Feels Native

* Operator overloading for `<<` and `>>` maps to send/recv.
* Does not replace or abstract away `await` - maintains explicit async behavior.
* Sane defaults, no monkey-patching, no metaclasses.

### Pythonic Error Handling

* `ChannelClosed` exception signals closure.
* `val, ok = await ch.receive()` pattern offers Go-style error recovery while remaining Pythonic.

### Explicit, Composable, Readable

* pychanio avoids black-box abstractions.
* Promotes composability by exposing primitives (channels, selects, sentinels) rather than frameworks.
* All primitives are interoperable with `asyncio`’s `Task`, `Future`, and coroutines.

---

## Design Trade-offs

| Feature                     | Status       | Reasoning/Justification                          |
| --------------------------- | ------------ | ------------------------------------------------ |
| Unbuffered channel blocking | Deferred     | Requires deeper changes to `asyncio` task flow   |
| Channel type safety         | Not enforced | Python is duck-typed; explicit checks encouraged |
| Select fairness tuning      | Minimal      | Non-determinism preferred for now                |
| Pipeline combinators        | Manual       | Prefer minimalism, users can compose themselves  |

---

## Summary

pychanio is built with **respect for both Go's concurrency model** and **Python’s language philosophy**. It neither tries to turn Python into Go nor treats Python as an afterthought. Instead, it creates a bridge between these two paradigms:

* Offering **Go’s expressive concurrency** tools
* While remaining **unapologetically Pythonic** in code style and usage

By staying minimal, composable, and explicit, pychanio lets Python developers adopt channel-based thinking without abandoning the ecosystem or learning curve they've already invested in.

---

We welcome future contributions that deepen Go compatibility, enhance performance, or broaden expressiveness-**but never at the cost of clarity, simplicity, or Python-first ergonomics.**
