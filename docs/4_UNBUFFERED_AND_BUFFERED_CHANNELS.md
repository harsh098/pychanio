# Chapter 4: Buffered vs Unbuffered Channels

One of the most powerful aspects of `pychanio` is its support for **buffered** and **unbuffered** channels. These determine the channel's capacity and control how coroutines interact with each other-whether they must block during sends and receives.

---

## Unbuffered Channels

By default, `chan()` creates an **unbuffered** channel:

```python
ch = chan()
```

Currently in `pychanio`, unbuffered channels behave like buffered channels with a size of 0-but do **not** yet block the sender until a receiver is ready (like in Go). This behavior is **planned** for future versions.

**Note:** In the current implementation, setting the channel capacity to 0 results in behavior equivalent to an **infinite buffer** under the hood. This is a workaround until proper blocking semantics are implemented for unbuffered channels.

### Characteristics (Current Behavior):

* Sends complete immediately even if no receiver is ready
* Messages can be lost if not promptly received
* Setting capacity to 0 actually creates an effectively unbounded queue

### Characteristics (Planned Behavior):

* Strong backpressure
* Ideal for tight coordination
* Mimics Go's default channel behavior

### Current Workaround for Synchronous Coordination:

To simulate blocking behavior until a receiver is ready, you can use an `asyncio.Event`, `await` on a nil channel, or use explicit signaling logic. Here’s a basic workaround using an extra coordination channel:

```python
import asyncio
from pychanio import chan, go

async def sender(ch, sync):
    print("sending...")
    ch << "data"
    await (sync >> None)  # wait until receiver signals done
    print("sent")

async def receiver(ch, sync):
    val = await (ch >> None)
    print(f"received: {val}")
    sync << True  # signal back to sender

async def main():
    ch = chan()
    sync = chan()
    go(sender, ch, sync)
    await receiver(ch, sync)

asyncio.run(main())
```

---

## Buffered Channels

You can specify a buffer size to allow the channel to queue messages:

```python
ch = chan(2)  # buffer size = 2
```

Buffered channels allow the sender to proceed without immediately blocking, up to the buffer capacity.

### Characteristics:

* Decouples producers from consumers
* Reduces blocking in high-throughput scenarios
* Mimics Go's `make(chan T, n)`
* **Sends block when the buffer is full**

### Example:

```python
import asyncio
from pychanio import chan, go, close

async def producer(ch):
    for i in range(3):
        print(f"sending: {i}")
        ch << i  # Schedules a send in the background, the task might get blocked in the background, if the buffer is full.
    close(ch)

async def consumer(ch):
    async for val in ch:
        await asyncio.sleep(0.3)
        print(f"received: {val}")

async def main():
    ch = chan(2)
    go(producer, ch)
    await consumer(ch)

asyncio.run(main())
```

Output:

```
sending: 0
sending: 1
sending: 2
received: 0
received: 1
received: 2
```

---

## Choosing the Right Type

| Use Case                           | Recommended Channel Type |
| ---------------------------------- | ------------------------ |
| Synchronous coordination           | Unbuffered (`chan()`) with a sync   |
| Decoupled producer-consumer flow   | Buffered (`chan(n)`)     |
| Batching or pipelining             | Buffered (`chan(n)`)     |

---

## What’s Next?

In the next chapter, we'll cover the use of `go(...)` to run background tasks, and how it relates to Go’s goroutines.

