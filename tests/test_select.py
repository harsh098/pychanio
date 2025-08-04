import pytest

from pychan import chan, select
from pychan.sentinels import DONE


@pytest.mark.asyncio
async def test_select_picks_ready_channel():
    ch1 = chan()
    ch2 = chan()

    ch1 << "fast"

    result = await select(
        (ch1 >> None, lambda val, ok: f"got1:{val}" if ok else "closed1"),
        (ch2 >> None, lambda val, ok: f"got2:{val}" if ok else "closed2"),
    )

    assert result == "got1:fast"


@pytest.mark.asyncio
async def test_select_with_default():
    ch = chan()

    result = await select(
        (ch >> None, lambda val, ok: "should_not_run"),
        default=lambda: "default_ran",
        timeout=0.01
    )

    assert result == "default_ran"


@pytest.mark.asyncio
async def test_select_timeout():
    ch = chan()

    with pytest.raises(TimeoutError):
        await select((ch >> None, lambda val, ok: val), timeout=0.1)


@pytest.mark.asyncio
async def test_select_done_signal():
    ch = chan()
    done = chan()
    done << DONE

    result = await select(
        (done >> None, lambda val, ok: DONE if val is DONE or not ok else None),
        (ch >> None, lambda val, ok: "should_not_run")
    )

    assert result == DONE
