# Chapter 5: Goroutines in Python with `go(...)`

In Go, goroutines are lightweight concurrent functions. In `pychan`, we offer a similar primitive using the `go(...)` helper function. This allows you to spawn background tasks easily within Python’s `asyncio` framework.

---

## What is `go(...)`?

The `go` function is a thin wrapper over `asyncio.create_task()` that starts an asynchronous coroutine in the background - much like launching a goroutine in Go.

```python
from pychan import go

go(coro, *args, **kwargs)
```

* `coro` is any `async def` function
* `*args` are passed directly to the coroutine
* `**kwargs` are passed directly to the coroutine

### Example:

```python
import asyncio
from pychan import go

async def worker(name):
    for i in range(3):
        await asyncio.sleep(0.5)
        print(f"{name} working {i}")

async def main():
    go(worker, "A")
    go(worker, "B")
    await asyncio.sleep(2)

asyncio.run(main())
```

Output:

```
A working 0
B working 0
A working 1
B working 1
A working 2
B working 2
```

---

## Advantages of `go(...)`

* Clean syntax for spawning concurrent tasks
* Avoids manual boilerplate of `asyncio.create_task()`
* Integrates well with channels and `select`

---

## Use With Channels

`go(...)` becomes even more powerful when combined with `chan()` and `select(...)`:

```python
from pychan import chan, go

async def sender(ch):
    ch << "hello"

async def receiver(ch):
    val = await (ch >> None)
    print(f"received: {val}")

async def main():
    ch = chan()
    go(sender, ch)
    await receiver(ch)

asyncio.run(main())
```

---

## What’s Next?

Now that you know how to launch concurrent tasks, in the next chapter we’ll explore `select(...)` - the foundation for writing non-blocking multi-channel logic, similar to Go’s `select` statement.

