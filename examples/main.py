import asyncio
from pychanio import (
    chan,
    close,
    split,
    go,
    select,
    nil,
)
from pychanio.sentinels import DONE


async def producer(name: str, ch) -> None:
    """
    Producer coroutine that sends 5 messages to the channel.
    """
    for i in range(5):
        msg = f"{name} -> message {i}"
        print(f"[{name}] sending: {msg}")
        ch << msg
        await asyncio.sleep(0.1)

    print(f"[{name}] closing channel.")
    close(ch)


async def consumer(name: str, ch) -> None:
    """
    Consumer coroutine that receives messages until the channel closes.
    """
    async for msg in ch:
        print(f"[{name}] received: {msg}")
    print(f"[{name}] done (channel closed).")


def done_signal_handler(val, ok):
    """
    Handler for done channel. When done is received, instruct the consumer to exit.
    """
    shutdown_signal = val is DONE or not ok
    if shutdown_signal:
        return DONE


async def fan_in_consumer(ch1, ch2, done):
    """
    Fan-in consumer using select. Terminates when `done` channel receives.
    """
    while True:
        try:
            result = await select(
                (done >> DONE, done_signal_handler),
                (
                    ch1 >> None,
                    lambda val, ok: f"[fan-in] from ch1: {val}"
                    if ok
                    else "[fan-in] ch1 closed",
                ),
                (
                    ch2 >> None,
                    lambda val, ok: f"[fan-in] from ch2: {val}"
                    if ok
                    else "[fan-in] ch2 closed",
                ),
                default=lambda: "[fan-in] nothing ready",
                timeout=0.3,
            )
            if result == DONE:
                print("[fan-in] shutdown signal received.")
                break
            print(result)
        except TimeoutError:
            print("[fan-in] timeout hit")
            break


async def nil_channel_demo():
    """
    Shows that nil channel blocks forever.
    """
    ch = nil()
    print("[nil-demo] Waiting on nil channel receive (will block forever)...")
    await (ch >> None)


async def main():
    # Create channels
    ch1 = chan(1)
    ch2 = chan(2)
    done = chan()

    # Split ch2 into send-only and receive-only for demonstration
    send_only, recv_only = split(ch2)

    # Launch producers
    go(producer, "Producer-1", ch1)
    go(producer, "Producer-2", send_only)

    # Launch consumers
    go(consumer, "Consumer-1", ch1)
    go(consumer, "Consumer-2", recv_only)

    # Signal shutdown after cumulative timeout
    async def signal_done_later():
        await asyncio.sleep(1.5)
        print("[main] sending done signal")
        done << DONE
        close(done)

    go(signal_done_later)

    # Fan-in consumer
    await fan_in_consumer(ch1, recv_only, done)

    # Uncomment to demo nil channel behavior
    # await nil_channel_demo()


if __name__ == "__main__":
    asyncio.run(main())
