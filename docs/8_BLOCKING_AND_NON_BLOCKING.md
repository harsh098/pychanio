# Chapter 8: Blocking and Non-blocking Operations

In this chapter, we explore **how and when operations on channels block** in pychanio, and how to structure your concurrency logic around these behaviors.

Understanding blocking behavior is critical to writing predictable and performant concurrent code. It determines **how tasks wait**, **when they yield**, and **how control flows** across coroutines.

---

## Overview

Every operation on a channel in `pychanio` is either:

* **Blocking** - waits until the operation completes.
* **Non-blocking** - initiates the operation and lets the caller proceed without waiting.

You can choose between the two depending on **what kind of control** and **task flow** you want to design.

---

## Blocking Send

```python
await ch.send(value)
```

This form of send **blocks** until the value is pushed successfully into the underlying queue.
Useful when
1. You want a guarantee that the item is successfully sent to the channel.

### Use Cases

* Ensures **backpressure**: producers slow down if consumers aren’t catching up
* Ideal for **rate-limited pipelines**
* Prevents buffer overflows

---

## Non-blocking Send

```python
ch << value  # equivalent to asyncio.create_task(ch.send(value))
```

This operation **does not block**. Instead, it:

* Schedules `ch.send(value)` as a background task
* Returns an `asyncio.Task` immediately

### Use Cases

* Fire-and-forget style messaging
* When backpressure is not a concern
* Logging, metrics pipelines, or loosely coupled fan-out
* Useful in *select* blocks for concurrent sends

### ⚠️ Caveats

* **Send errors are not immediate**: If the channel is closed, the task may still attempt to send. The exception (e.g., `ChannelClosed`) will be raised **within the task**, not synchronously.
* **Potential race with close**: It's possible that `ch << value` is scheduled before `close(ch)` but executes after. In such cases, the value **may still be delivered** even after closure.
* This behavior is **intentional**: It provides performance and flexibility similar to actor-style fire-and-forget systems. If strict send guarantees are required, use `await ch.send(value)` instead.

---

## Blocking Receive

```python
value = await ch.receive()
```

This form **blocks the current coroutine** until a value is available.

If the channel is:

* **Closed but not empty** → Waits until the value is available.
* **Empty and closed** → returns (None,False) tuple
* **Nil** → blocks forever

### Example

```python
async def consumer(ch):
    val = await ch.receive()
    print("Received:", val)
```

### Use Cases

* Sequential logic where you **must wait** for the next item
* Ensures **deterministic flow**
* Cleaner than callbacks or polling

---

## DSL-style Blocking Receive

```python
value = await (ch >> None)
```

This is a syntactic sugar for `await ch.receive()`.

It mimics Go's `val := <-ch` syntax.

⚠️ **Reminder**: You must wrap it in parentheses due to Python's operator precedence.

---

## Non-blocking Receive via Select

pychanio doesn't provide a dedicated `try_receive()` or `.empty()` check.

However, non-blocking receive is best expressed using `select(...)`:

```python
result = await select(
    (ch.receive(), lambda val, ok: val),
    default=lambda: "nothing ready"
)
```  

Or, if you prefer DSL-Style syntax

```python
result = await select(
    (ch >> _, lambda val, ok: val),
    default=lambda: "nothing ready"
)
```  

### Use Cases

* Polling multiple channels without blocking
* Implementing timeouts or default behaviors
* Event-driven systems

---

## Nil Channels and Blocking

A **nil channel** blocks on both send and receive operations **forever**:

```python
ch = nil()

await ch.send(42)      # Blocks forever
await ch.receive()     # Blocks forever
```

Nil channels are useful in scenarios like:

* Disabling a case in `select`
* Signaling shutdown using indirection
* Testing blocking behavior

---

## Summary

| Operation              | Blocking | Notes                                               |
| ---------------------- | -------- | --------------------------------------------------- |
| `await ch.send(val)`   | Yes      | Suspends until send completes                       |
| `ch << val`            | No       | Schedules send as task, no backpressure             |
| `await ch.receive()`   | Yes      | Suspends until value available or channel is closed |
| `await (ch >> None)`   | Yes      | DSL sugar for blocking receive                      |
| `select(..., default)` | No       | Non-blocking if default provided                    |
| `await select(...)`    | Yes      | Blocks until any case is ready                      |

---

## Coming Up Next

Now that you understand how blocking and non-blocking operations work in `pychanio`, we can dive into **Concurrency Patterns** - building blocks like fan-in, fan-out, pipelines, and pub-sub.
