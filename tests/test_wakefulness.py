import time
from unittest.mock import patch

from eugeroic import wakefulness

def test_wakefulness():
    # There's not much we can to test here, but we can at least make sure
    # that the module is importable.
    with wakefulness("A test message"):
        time.sleep(0.1)


def test_wakefulness_logging_on_entry_positive(caplog):
    caplog.set_level("DEBUG")
    with wakefulness("A test message"):
        assert "Entering wakefulness state during: 'A test message'" in caplog.text
        time.sleep(0.1)


def test_wakefulness_logging_on_entry_negative(caplog):
    caplog.set_level("DEBUG")
    assert "Entering wakefulness state during: 'A test message'" not in caplog.text
    with wakefulness("A test message"):
        time.sleep(0.1)


def test_wakefulness_logging_on_exit_positive(caplog):
    caplog.set_level("DEBUG")
    with wakefulness("A test message"):
        time.sleep(0.1)
    assert "Exiting wakefulness state after: 'A test message'" in caplog.text


def test_wakefulness_logging_on_exit_negative(caplog):
    caplog.set_level("DEBUG")
    with wakefulness("A test message"):
        time.sleep(0.1)
        assert "Exiting wakefulness state after: 'A test message'" not in caplog.text
