## Chapter 7: Sentinels - Control Signals in PyChan

In complex concurrent systems, it’s not enough to send only data between goroutines-**we often need to signal intent**, such as *shutdown*, *cancellation*, or *heartbeat*. PyChan offers a clean and idiomatic way to accomplish this using **sentinels**.

---

### What are Sentinels?

A **Sentinel** is a unique, singleton-like object used to convey **control messages** through channels. Unlike regular data, sentinels:

* Are **identity-comparable** (`msg is DONE`)
* Are **self-documenting** (e.g., `<Signal: CANCEL>`)
* Allow for **typed control flow** without magic strings

These are critical for implementing robust shutdown signals, cancellation of operations, and keep-alive logic in pipelines.

---

### Predefined Sentinels in PyChan

PyChan provides three built-in signals in `pychan.sentinels`:

| Sentinel    | Purpose                            |
| ----------- | ---------------------------------- |
| `DONE`      | Indicates completion or shutdown   |
| `CANCEL`    | Requests cancellation of operation |
| `HEARTBEAT` | Used for liveness or ping signals  |

```python
from pychan.sentinels import DONE, CANCEL, HEARTBEAT
```

---

### Example: Sending a Shutdown Signal

```python
from pychan import chan, close
from pychan.sentinels import DONE

async def worker(ch):
    async for msg in ch:
        if msg is DONE:
            print("Received shutdown signal")
            break
        print(f"Working on: {msg}")

ch = chan()
await (ch << "task-1")
await (ch << DONE)
close(ch)
await worker(ch)
```

---

### Detecting Sentinels in Pipelines

Use the utility function `is_signal(obj)` to identify if a received message is a sentinel:

```python
from pychan.sentinels import is_signal

async for msg in ch:
    if is_signal(msg):
        print(f"Received control signal: {msg}")
    else:
        process(msg)
```

This avoids hard-coding identity checks (`msg is ...`) and lets you apply generic logic across all sentinels.

---

### Fan-In Use Case with Select and Sentinels

Sentinels pair especially well with `select()` to provide structured exits for pipelines:

```python
from pychan import select
from pychan.sentinels import DONE

async def fan_in_consumer(ch1, ch2, done):
    while True:
        result = await select(
            (done >> DONE, lambda val, ok: DONE),
            (ch1 >> None, lambda val, ok: val if ok else None),
            (ch2 >> None, lambda val, ok: val if ok else None),
        )
        if result is DONE:
            print("Shutdown requested")
            break
        print(f"Received: {result}")
```

---

### Why Use Sentinels Instead of Strings?

While you *can* use plain strings like `"done"` or `"cancel"`, sentinels provide stronger guarantees:

* ✅ **Identity comparison** is faster and safer than string matching.
* ✅ **Singletons** prevent accidental overwrites.
* ✅ **Self-describing** for debugging and logging.
* ✅ **Extensible**: define your own!

---

### Defining Custom Sentinels

You can define your own using the `Sentinel` class:

```python
from pychan.sentinels import Sentinel

RETRY = Sentinel("RETRY")
```

Use this in the same way as built-ins.

---

### Summary

| Feature                       | Benefit                           |
| ----------------------------- | --------------------------------- |
| `DONE`, `CANCEL`, `HEARTBEAT` | Built-in lifecycle signals        |
| `Sentinel(name)`              | Create custom signal objects      |
| `is_signal(x)`                | Generalized signal detection      |
| Identity comparison           | Faster, safer than string matches |

Sentinels are a key part of PyChan’s philosophy of **structured concurrency** and **predictable control flow**.

---

### Up Next

In the next chapters, we’ll explore **Blocking and non blocking operations** and  **real-world concurrency patterns** using all the pieces we’ve explored so far-channels, select blocks, goroutines, and sentinels.
