import contextlib
from collections.abc import Generator

from eugeroic.drivers.macos.iokit import power_management_assertion, AssertionType, Level

@contextlib.contextmanager
def wakefulness(logger, reason: str) -> Generator[None, None, None]:
    logger.debug("Entering wakefulness state during: %r", reason)
    try:
        with power_management_assertion(AssertionType.PreventUserIdleDisplaySleep, Level.On, reason):
            yield
    finally:
        logger.debug("Exiting wakefulness state after: %r", reason)
