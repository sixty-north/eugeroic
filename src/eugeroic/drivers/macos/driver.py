import contextlib
from collections.abc import Generator

from eugeroic.drivers.macos.iokit import (
    power_management_assertion, AssertionType, Level,
    declare_local_user_activity,
)


@contextlib.contextmanager
def wakefulness(logger, reason: str, wake: bool=True) -> Generator[None, None, None]:
    logger.debug("Entering wakefulness state during: %r", reason)
    try:
        with power_management_assertion(AssertionType.PreventUserIdleDisplaySleep, Level.On, reason):
            if wake:
                declare_local_user_activity(reason)
            yield
    finally:
        logger.debug("Exiting wakefulness state after: %r", reason)
