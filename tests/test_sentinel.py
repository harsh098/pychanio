from pychan.sentinels import DONE, CANCEL, HEARTBEAT, is_signal, Sentinel


def test_is_signal_true_for_builtins():
    assert is_signal(DONE)
    assert is_signal(CANCEL)
    assert is_signal(HEARTBEAT)


def test_is_signal_false_for_regular_values():
    assert not is_signal("hello")
    assert not is_signal(42)


def test_custom_sentinel_identity():
    RESTART = Sentinel("RESTART")
    assert is_signal(RESTART)
    assert str(RESTART) == "RESTART"
    assert repr(RESTART) == "<Signal: RESTART>"
