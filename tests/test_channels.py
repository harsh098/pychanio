import pytest
import asyncio

from pychanio import chan, close, split, go
from pychanio.exceptions import ChannelClosed


@pytest.mark.asyncio
async def test_unbuffered_channel_send_receive():
    ch = chan()

    async def sender():
        ch << "hello"

    async def receiver():
        val, ok = await (ch >> None)
        assert ok
        assert val == "hello"

    await asyncio.gather(sender(), receiver())


@pytest.mark.asyncio
async def test_buffered_channel_ordering():
    ch = chan(2)
    ch << "a"
    ch << "b"
    val1, ok1 = await (ch >> None)
    val2, ok2 = await (ch >> None)
    assert ok1 and ok2
    assert (val1, val2) == ("a", "b")


@pytest.mark.asyncio
async def test_channel_close_behavior():
    ch = chan(1)
    await ch.send("last")
    close(ch)
    val, ok = await (ch >> None)
    assert not ok
    assert val == "last"

    val, ok = await (ch >> None)
    assert not ok
    assert val is None

    with pytest.raises(ChannelClosed):
        ch << "should_fail"


@pytest.mark.asyncio
async def test_split_send_receive():
    ch = chan()
    send, recv = split(ch)

    send << 123
    val, ok = await (recv >> None)
    assert ok
    assert val == 123
