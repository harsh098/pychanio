# pychanio

Go-style **channels** and **select blocks** for Python’s `asyncio`.

**pychanio** brings structured concurrency to Python, inspired by Go. It provides `chan`, `select`, `go`, and control signals like `DONE` and `CANCEL`.

## ✅ Features

- Full-duplex and directional channels
- Buffered and unbuffered behavior
- `<<` and `>>` DSL syntax for send/receive
- Go-style `select()` block with timeout and default
- Background goroutines with `go(fn)`
- Built-in sentinels for clean shutdown
- Works with native `asyncio`

## 📦 Installation

```bash
pip install pychanio
```

## 🔁 Example

```python
import asyncio
from pychanio import chan, go, close

async def producer(ch):
    for i in range(3):
        ch << i
    close(ch)

async def consumer(ch):
    async for val in ch:
        print(val)

async def main():
    ch = chan()
    go(producer, ch)
    await consumer(ch)

asyncio.run(main())
```

## 📚 Docs

Find the docs here at: 
[harsh-mishra.gitbook.io/pychanio](https://harsh-mishra.gitbook.io/pychanio)

## 🛠 Requirements

* Python 3.8+
* `asyncio`

## 📄 License

MIT © 2025 Harsh Mishra
