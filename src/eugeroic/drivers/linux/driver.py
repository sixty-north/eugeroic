import contextlib
from collections.abc import Generator


@contextlib.contextmanager
def wakefulness(logger, reason: str) -> Generator[None, None, None]:
    """A context manager which prevents the display from sleeping.
    """
    logger.debug("Entering wakefulness state during: %r", reason)
    logger.debug("Unsupported attempt to enter wakefulness state during (not yet implemented on Linux): %r", reason)
    # TODO: We can do this with DBus. There is some information here:
    #       https://stackoverflow.com/questions/31498114/how-to-programmatically-prevent-linux-computer-from-sleeping-or-turning-on-scree
    #       https://gist.github.com/Vineg/eca223fbf478a3c806444a13e538a9fc
    try:
        yield
    finally:
        logger.debug("Exiting wakefulness state after: %r", reason)
        logger.debug("Unsupported attempt to exit wakefulness state during (not yet implemented on Linux): %r", reason)


