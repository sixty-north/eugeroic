import sys
import contextlib
import logging
from collections.abc import Generator

logger = logging.getLogger(__name__)

platform = sys.platform.lower()
if platform == "win32":
    from .windows.driver import wakefulness as _wakefulness
elif platform == "darwin":
    from .macos.driver import wakefulness as _wakefulness
elif platform.startswith("linux"):
    from .linux.driver import wakefulness as _wakefulness
else:
    from .null.driver import wakefulness as _wakefulness


@contextlib.contextmanager
def wakefulness(reason: str) -> Generator[None, None, None]:
    """A context manager which prevents the display from sleeping.

    Note:
        This will not awaken the display if it is already asleep.

    Args:
        reason: The reason for keeping the display awake.
    """
    with _wakefulness(logger, reason):
        yield


__all__ = ["wakefulness"]
