# Chapter 3: Channel Types and Interfaces

`pychan` supports multiple channel types to model safe communication across coroutines. In this chapter, we'll explore the available channel interfaces and learn how to control access using the `split()` function.

---

## Channel Types

At the core, all channels in `pychan` are full-duplex (send + receive). But you can split them into directional views for better safety and intent clarity:

### 1. Full-Duplex Channel

Created using:

```python
ch = chan()
```

You can both send and receive from this channel.

```python
ch << value           # send
await (ch >> None)    # receive
```

### 2. Send-Only Channel

Created via:

```python
send_only, _ = split(ch)
```

You can only send on this channel.

```python
send_only << value
```

Attempting to receive from a send-only channel will raise an error.

### 3. Receive-Only Channel

Created via:

```python
_, recv_only = split(ch)
```

You can only receive from this channel.

```python
await (recv_only >> None)
```

Sending to a receive-only channel is not permitted.

### 4. Nil Channels

> `nil` channels will be discussed in [Chapter 4.](CONCURRENCY_PATTERNS.md)

---

## Using `split()` Safely

The `split()` function provides two views of a channel:

```python
send_ch, recv_ch = split(chan())
```

This is especially useful when you want to expose only one direction of communication to a function:

```python
async def producer(send_ch):
    send_ch << "data"

async def consumer(recv_ch):
    msg = await (recv_ch >> None)
    print(msg)
```

This models the Go pattern of passing `chan<-` and `<-chan` types to coroutines, helping avoid accidental misuse.

---

## Channel Capabilities Summary

| Channel     | Can Send | Can Receive | Datatype |
| ----------- | -------- | ----------- | --------- |
| `chan()`    | ✅        | ✅           | `ChannelDSL` |
| `send_only` | ✅        | ❌           | `SendOnlyChannel` |
| `recv_only` | ❌        | ✅           | `ReceiveOnlyChannel` |

---

## Practical Example

```python
import asyncio
from pychan import chan, split, go

async def producer(send_ch):
    for i in range(5):
        send_ch << f"value-{i}"
        await asyncio.sleep(0.1)

async def consumer(recv_ch):
    async for val in recv_ch:
        print(f"got: {val}")

async def main():
    ch = chan()
    send_ch, recv_ch = split(ch)
    go(producer, send_ch)
    await consumer(recv_ch)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Coming Up Next

In the next chapter, we'll explore **buffered vs unbuffered channels** and how to use them for controlling throughput and backpressure.
