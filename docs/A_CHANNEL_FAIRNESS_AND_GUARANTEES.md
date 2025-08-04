
# Chapter 10: Channel Fairness and Guarantees

Channel-based concurrency introduces questions about fairness, ordering, and delivery guarantees-especially in systems with multiple producers, consumers, or `select()` blocks competing over shared channels.

In `pychan`, we follow Go-inspired semantics where possible, but also document any deviations explicitly. This chapter discusses what guarantees are provided today, and which are deferred to future versions.

---

## 1. Message Delivery Guarantees

### ✅ Guarantee: Messages Sent Before Close Are Delivered

If a channel is **not closed** and a producer successfully sends a message (`await ch.send(x)` or `ch << x`), that message will be eventually delivered to a receiver, unless the consumer exits early.

```python
ch = chan()
go(lambda: ch << "msg")
val, ok = await (ch >> None)
# val == "msg", ok == True
```

### ✅ Guarantee: Closure Prevents Further Sends

If a channel is closed via `close(ch)`, any subsequent send attempt raises `ChannelClosed`. Receivers may still read buffered items (if any), but no new data may be written.

```python
close(ch)
ch << "oops"  # Raises ChannelClosed
```

---

## 2. FIFO Ordering

Each `pychan` channel uses an internal `asyncio.Queue`, which guarantees **FIFO (first-in-first-out)** ordering:

```python
ch = chan()
await ch.send(1)
await ch.send(2)

v1, _ = await (ch >> None)
v2, _ = await (ch >> None)
# v1 == 1, v2 == 2
```

This guarantee **applies per channel**, but not across channels.

---

## 3. Select Fairness

### ❌ No Strong Fairness Across Select Cases

When multiple channel operations are passed to `select(...)`, `pychan` **randomly chooses one** of the ready cases. This means:

* You cannot assume round-robin scheduling
* Some branches may be selected more frequently than others
* Starvation is *possible* in certain configurations

#### Example

```python
await select(
    (ch1 >> None, lambda v, ok: print("from ch1")),
    (ch2 >> None, lambda v, ok: print("from ch2")),
)
```

Even if both channels are ready, the selection is random.

### Design Rationale

This behavior is **intentional** and mirrors Go’s design:

> *Select statements choose randomly among equally ready channels to prevent deterministic, fragile patterns.*

If fairness is required, it must be enforced by user code (e.g., shuffle cases manually or alternate across calls).

---

## 4. Unbuffered Channels ≠ Blocking (Yet)

Unlike Go, **unbuffered channels in `pychan` do not currently block the sender** until a receiver is ready.

Instead, `chan()` (with capacity = 0) behaves as if it has an **infinite buffer**.

### Characteristics (Current Behavior):

* Sends complete immediately, regardless of receiver readiness
* Receivers can read at any later point
* No backpressure or flow control
* Behaves like an unbounded queue internally

This is a **known limitation** and will be addressed in a future version. For now, do not rely on unbuffered channels for tight coordination.

See [Chapter 4](./4_UNBUFFERED_AND_BUFFERED_CHANNELS.md) for detailed workarounds and explanation.

---

## 5. Buffered Channels and Blocking

Buffered channels (e.g., `chan(2)`) **do** block the sender once the buffer is full. This enables:

* Flow control between fast producers and slow consumers
* Controlled throughput in pipelines

```python
ch = chan(2)
await ch.send("a")  # succeeds immediately
await ch.send("b")  # succeeds immediately
await ch.send("c")  # blocks until a value is received
```

Receivers always block if the channel is empty.

---

## 6. Starvation and Manual Fairness

If fairness across channels matters to your application, consider:

### ✅ Manual Shuffling in Select

```python
import random
cases = [(ch1 >> None, handle1), (ch2 >> None, handle2)]
random.shuffle(cases)
await select(*cases)
```

### ✅ Round-Robin Consumer

```python
channels = [ch1, ch2, ch3]
i = 0

while True:
    ch = channels[i % len(channels)]
    val, ok = await (ch >> None)
    process(val)
    i += 1
```

---

## 7. Summary of Guarantees

| Behavior                            | Guarantee? | Notes                                       |
| ----------------------------------- | ---------- | ------------------------------------------- |
| FIFO ordering per channel           | ✅          | Enforced via `asyncio.Queue`                |
| Delivery before closure             | ✅          | All sent messages are received before close |
| Send after close                    | ❌          | Raises `ChannelClosed`                      |
| Blocking on unbuffered channel send | ❌          | Not implemented yet (no backpressure)       |
| Blocking on buffered full channel   | ✅          | Sender waits if buffer is full              |
| Select branch fairness              | ❌          | Selection is random                         |
| Receive from nil channel            | ⚠️         | Blocks forever                              |

---

## 8. Related Examples

See [`examples/main.py`](../examples/main.py):

```python
await fan_in_consumer(ch1, ch2, done)

# select block with timeout and default
await select(
    (ch1 >> None, lambda v, ok: f"from ch1: {v}"),
    (ch2 >> None, lambda v, ok: f"from ch2: {v}"),
    timeout=0.2,
    default=lambda: "idle",
)
```

---

## 9. Looking Ahead

Future enhancements may include:

* Proper backpressure for unbuffered channels
* Weighted or priority-based select
* Explicit fairness guarantees for select blocks

For now, `pychan` prioritizes **clarity and simplicity**, matching Go's concurrency model where possible while documenting deviations clearly.

---