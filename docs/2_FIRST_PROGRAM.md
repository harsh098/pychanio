# Chapter 2: Your First Channel Program

Let's build a simple producer-consumer example using `pychan`.

```python
import asyncio
from pychan import chan, go, close

async def producer(ch):
    for i in range(3):
        msg = f"msg-{i}"
        print(f"Producing: {msg}")
        ch << msg  # async send
        await asyncio.sleep(0.2)
    close(ch)  # close the channel

async def consumer(ch):
    async for msg in ch:
        print(f"Consumed: {msg}")

async def main():
    ch = chan()
    go(producer, ch)
    await consumer(ch)

if __name__ == "__main__":
    asyncio.run(main())
```

### Output:

```
Producing: msg-0
Consumed: msg-0
Producing: msg-1
Consumed: msg-1
Producing: msg-2
Consumed: msg-2
```

### Explanation:

* `chan()` creates an unbuffered channel
* `ch << msg` asynchronously sends a value
* `async for msg in ch:` receives until the channel is closed
* `go(...)` spawns the producer in the background

This small example shows how channels coordinate producer-consumer patterns naturally and efficiently.

---

## Next Chapter

We'll now explore different **types of channels** (full-duplex, send-only, receive-only), and how to use `split()` to control access.
