import contextlib
from collections.abc import Generator

from eugeroic.drivers.linux.bus import inhibited_screensaver


@contextlib.contextmanager
def wakefulness(logger, reason: str, wake: bool=True) -> Generator[None, None, None]:
    """A context manager which prevents the display from sleeping.
    """
    logger.debug("Entering wakefulness state during: %r", reason)
    try:
        with inhibited_screensaver(reason, wake=wake):
            yield
    finally:
        logger.debug("Exiting wakefulness state after: %r", reason)
