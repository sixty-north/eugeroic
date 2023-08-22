import contextlib
from collections.abc import Generator

from eugeroic.drivers.windows.display import inhibit_screensaver, uninhibit_screensaver


@contextlib.contextmanager
def wakefulness(logger, reason: str) -> Generator[None, None, None]:
    """A context manager which prevents the display from sleeping.
    """
    logger.debug("Entering wakefulness state during: %r", reason)
    inhibit_screensaver()
    try:
        yield
    finally:
        logger.debug("Exiting wakefulness state after: %r", reason)
        uninhibit_screensaver()
