# Chapter 6: Select Blocks for Non-Blocking Logic

The `select()` function in **PyChan** brings Go-style non-deterministic concurrency control to Python’s `asyncio`. This chapter explores the `select` block’s design, semantics, and practical usage.

---

## Overview

`select()` allows a coroutine to wait on multiple channel operations concurrently and react to the first one that becomes ready.

### Syntax

```python
await select(
    (awaitable, handler),
    ...,
    default=callable,      # optional
    timeout=float          # optional
)
```

Each case is a tuple:

* `awaitable`: usually a channel receive operation like `ch >> None`
* `handler`: a function `(val, ok) -> result` that processes the result

The return value from `select()` is the return value of the selected handler.

---

## Core Semantics

Each call to `select(...)` evaluates a list of channel operations and picks one *randomly* among the ready ones. You can provide:

* Multiple **channel cases**
* An optional `default` handler
* An optional `timeout` in seconds

---

## `select()` Behavior Scenarios

### 1. **No Timeout and No Default**

Waits indefinitely until **any channel** has a message.

```python
result = await select(
    (ch1 >> None, handle_ch1),
    (ch2 >> None, handle_ch2),
)
```

* Blocks until at least one channel has data.
* Picks one **randomly** if multiple are ready.

---

### 2. **No Timeout and Default**

Returns immediately if **no channels are ready**.

```python
result = await select(
    (ch1 >> None, handle_ch1),
    (ch2 >> None, handle_ch2),
    default=lambda: "nothing to do",
)
```

* If no channels have data: `default()` is invoked.
* If one or more are ready: picks one randomly and invokes handler.

---

### 3. **Timeout but No Default**

Waits for a given time, then raises `TimeoutError` if no cases complete.

```python
try:
    result = await select(
        (ch1 >> None, handle_ch1),
        timeout=1.0
    )
except TimeoutError:
    print("select timed out")
```

* Ensures bounded wait time.
* Useful for slow producers or graceful fallbacks.

---

### 4. **Timeout and Default**

Behaves like Go’s `select` with `time.After`.

```python
result = await select(
    (ch1 >> None, handle_ch1),
    timeout=2.0,
    default=lambda: "fallback result",
)
```

* Waits for `timeout` seconds.
* If no case completes, falls back to `default()` instead of raising.

---

## Nil Channels in Select

Nil channels **never unblock**, making them perfect for disabling select cases dynamically:

```python
ch = chan() if condition else nil()

result = await select(
    (ch >> None, handle_data),
    default=lambda: "skip"
)
```

If `condition` is `False`, that case is ignored at runtime due to `nil`'s infinite blocking behavior.

### Example: Disabling a Branch

```python
ch1 = chan()
ch2 = nil()  # disable this branch

result = await select(
    (ch1 >> None, lambda val, ok: f"got {val}"),
    (ch2 >> None, lambda val, ok: "should never be picked"),
    timeout=1
)
```

---

## Handling Channel Closure

Each handler receives a second argument: `ok`, which is `False` if the channel is closed and empty.

```python
def handle(val, ok):
    if not ok:
        return "channel closed"
    return f"got {val}"
```

Always check `ok` to safely distinguish between data and shutdown.

---

## Example: Coordinated Fan-In

```python
async def fan_in_consumer(ch1, ch2, done):
    while True:
        result = await select(
            (done >> None, lambda val, ok: DONE if val is DONE or not ok else None),
            (ch1 >> None, lambda val, ok: f"ch1: {val}" if ok else "ch1 closed"),
            (ch2 >> None, lambda val, ok: f"ch2: {val}" if ok else "ch2 closed"),
            default=lambda: "idle",
            timeout=1.0,
        )
        if result == DONE:
            print("shutting down")
            break
        print(result)
```

*Note: The `DONE` sentinel is introduced in Chapter 7.*

---

## Best Practices

* Use `default` to implement **non-blocking polls**
* Use `timeout` for **bounded waits**
* Use `nil()` to **disable branches dynamically**
* Check `ok` to detect **channel closure**
* Return meaningful values from handlers and propagate via `select()`

