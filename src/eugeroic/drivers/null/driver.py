import contextlib
from collections.abc import Generator


@contextlib.contextmanager
def wakefulness(logger, reason: str) -> Generator[None, None, None]:
    """A context manager which prevents the display from sleeping.
    """
    logger.debug("Entering wakefulness state during: %r", reason)
    logger.debug("Unsupported attempt to enter wakefulness state during: %r", reason)
    try:
        yield
    finally:
        logger.debug("Exiting wakefulness state after: %r", reason)
        logger.debug("Unsupported attempt to exit wakefulness state during : %r", reason)
