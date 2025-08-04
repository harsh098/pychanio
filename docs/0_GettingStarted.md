# Getting Started with `pychan`

Welcome to **pychan**, a concurrency library that brings Go-style channels and `select` semantics to Python's `asyncio` world.

This guide will help you get started with the core concepts, installation steps, and writing your first channel-based program in Python. Whether you're familiar with Go or completely new to channel-based concurrency, this guide aims to make `pychan` accessible and intuitive.

---

## What is `pychan`?

`pychan` is a Python library designed to mimic Go's concurrency primitives:

* **Channels** for coroutine-safe communication
* **Goroutines** via `go(...)`
* **`select` blocks** for non-deterministic choice across multiple awaitables
* **Nil channels** that block forever
* **Sentinels** like `DONE`, `CANCEL`, and `HEARTBEAT` for control flow

With `pychan`, you can write concurrent code that is expressive, safe, and idiomatic-leveraging Python's `asyncio` without callbacks or tangled task management.

---

## Why use `pychan`?

Python's built-in `asyncio.Queue` is powerful but lacks Go-style channel semantics:

* **Explicit closing** of queues
* **Backpressure via blocking sends**
* **Separate send-only and receive-only views**
* **Composable `select` blocks**

`pychan` builds on top of `asyncio` to provide:

* Go-like concurrency in idiomatic Python
* Simplified coordination between producers and consumers
* Clearer patterns for cancellation and shutdown

---

## Core Concepts

Fundamental operations with `pychan`:

| Operation            | Description                                                     |
| -------------------- | --------------------------------------------------------------- |
| `chan()`             | Creates a full-duplex channel (buffered/unbuffered)             |
| `ch << val`          | Asynchronously sends `val` into the channel                     |
| `await ch.send()`    | Synchronously sends `val` into the channel                      |
| `await ch.receive()` | Receives a value from the channel                               |
| `await (ch >> None)` | Receives a value from the channel (DSL Syntax)                  |
| `go(fn)`             | Spawns a coroutine in the background (like Go's `go fn()`)      |
| `select(...)`        | Waits on multiple channels and executes the first ready handler |
| `nil()`              | Creates a channel that blocks on all operations                 |

---

## When to Use It

Use `pychan` when:

* You're coordinating multiple async producers/consumers
* You need fine-grained backpressure control
* You want to fan-in or fan-out data across tasks
* You want readable, Go-inspired concurrency in Python

Don't use it when:

* You need multiprocessing or inter-process communication
* You’re already using threading primitives (e.g., `queue.Queue`)

---

## Next Chapter

In the next chapter, we'll walk through how to install `pychan` and verify your environment is ready to write concurrent code using channels.

