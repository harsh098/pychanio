
# Chapter 9: Concurrency Patterns

In this chapter, we explore powerful concurrency patterns enabled by `pychan`. These patterns mirror familiar idioms from Go, such as fan-in, fan-out, graceful shutdown, and timeouts. The goal is to equip you with practical tools for building robust, expressive concurrent programs in Python.

---

## 🔀 Fan-In

Fan-in is a pattern where multiple producers send data into a single consumer. `pychan.select()` enables clean coordination across these inputs.

### Example

```python
async def fan_in_consumer(ch1, ch2, done):
    while True:
        result = await select(
            (done >> DONE, lambda v, ok: DONE),
            (ch1 >> None, lambda v, ok: f"[fan-in] from ch1: {v}" if ok else None),
            (ch2 >> None, lambda v, ok: f"[fan-in] from ch2: {v}" if ok else None),
            default=lambda: "[fan-in] nothing ready",
            timeout=0.2,
        )
        if result == DONE:
            break
        print(result)
```

This lets you merge messages from multiple channels, with optional timeout or cancellation.

---

## 🍴 Fan-Out

Fan-out distributes data from a single channel to multiple workers or consumers.

```python
async def worker(name, ch):
    async for msg in ch:
        print(f"[{name}] received: {msg}")

ch = chan()
for i in range(3):
    go(worker, f"worker-{i}", ch)

for i in range(10):
    ch << f"msg-{i}"

close(ch)
```

Each worker receives messages from the shared channel concurrently.

---

## ✅ Graceful Shutdown

To stop workers or loops cleanly, you can use sentinels like `DONE` or detect when a channel is closed.

```python
from pychan.sentinels import DONE

async def shutdown_listener(done_ch):
    async for msg in done_ch:
        if msg is DONE:
            print("Shutting down...")
            break
```

You can pair this with a signaler:

```python
# Signal shutdown after cumulative timeout
async def shutdown_signal():
    await asyncio.sleep(1.5)
    print("[main] sending done signal")
    done << DONE
    close(done)

go(shutdown_signal)
```

---

## ⏱ Timeouts and Defaults

In real systems, you often want to avoid waiting forever. `pychan.select()` provides both `timeout` and `default` handlers:

```python
result = await select(
    (ch >> None, lambda v, ok: v if ok else "closed"),
    timeout=0.5,
    default=lambda: "nothing happened",
)
```

If no case becomes ready in `0.5s`, the `default` branch is executed instead.

---

## 🚫 Disabling Select Cases with Nil Channels

Sometimes, you want to conditionally *disable* a select case. You can do this by replacing the channel with `nil()`.

```python
ch = nil()  # will block forever

await select(
    (ch >> None, lambda v, ok: ...),  # effectively disabled
    default=lambda: "fallthrough",
)
```

This avoids complex conditional logic inside `select`.

---

## 🪝 Pipeline Composition

You can build multi-stage pipelines where each stage is a coroutine and communicates over channels.

```python
async def stage1(out):
    for i in range(3):
        out << i
    close(out)

async def stage2(inp, out):
    async for val in inp:
        out << val * 2
    close(out)

async def stage3(inp):
    async for val in inp:
        print(f"final: {val}")

ch1 = chan()
ch2 = chan()

go(stage1, ch1)
go(stage2, ch1, ch2)
await stage3(ch2)
```

Each stage operates independently and concurrently, making the pipeline highly modular.

---

## 🧪 Pattern Combinations

All these patterns can be composed freely:

* Use **fan-in** for aggregating from producers.
* Apply **timeouts** or **defaults** to avoid stalling.
* Add **shutdown sentinels** for lifecycle management.
* Use **nil channels** for dynamic enabling/disabling of select branches.
* Construct **pipelines** for multi-stage processing.

---

## ✅ Summary

| Pattern       | Purpose                          | Core Tools                   |
| ------------- | -------------------------------- | ---------------------------- |
| Fan-In        | Merge inputs from many producers | `select`, multiple `>>`      |
| Fan-Out       | Distribute to many consumers     | shared channel + `go()`      |
| Graceful Exit | Controlled shutdown              | `sentinels.DONE`, `close()`  |
| Timeouts      | Avoid infinite wait              | `select(..., timeout=...)`   |
| Defaults      | Fallback behavior                | `select(..., default=...)`   |
| Nil Channels  | Dynamically disable select cases | `nil()`                      |
| Pipelines     | Modular multi-stage processing   | chained `go()`s and channels |

---

## What's Next?

Next up, we'll explore **channel fairness and scheduling guarantees**-how PyChan’s `select` and `go` balance concurrent flows.

