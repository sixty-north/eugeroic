from contextlib import asynccontextmanager, contextmanager
import logging
import sys
import asyncio
import threading
import concurrent.futures
from typing import Optional
import time

from dbus_next.aio import MessageBus
from dbus_next.errors import (
    InvalidAddressError,
    InvalidIntrospectionError,
    InvalidInterfaceNameError,
    InvalidBusNameError,
    InvalidObjectPathError,
    InvalidMemberNameError,
)

logger = logging.getLogger(__name__)

# This code is particularly convoluted because we want to use the dbus_next package
# which is async, but we don't want to force the callers of this function to be async
# as well. So we start a separate thread with its own event loop, run the async stuff,
# and then shut it down.
#
# We also can't call Inhibit with one bus connection, retain the cookie, and call UnInhibit [sic]
# with another bus connection, because the cookie is only valid for the connection it was
# created on. So we need to maintain the bus connection for the duration of the context manager.
#
# Additional complexity is added by the fact that we want to be able to raise exceptions
# from the async code in the main thread, so we need to use threading.Event to signal
# when the async code has finished, and then raise the exception in the main thread.
#
# Finally, we want to be able to use this code as a context manager, so we need to
# be able to signal as the async code progresses and when the async code has finished, and then
# wait in the main thread for those signals.
#
# Finally, a D-Bus may not be available, so we need to be able to fall back to a fake implementation
# if the real one isn't available to allow the implementation to proceed gracefully (and be tested
# in environments without a D-Bus). Even if the D-Bus is available, the required endpoints may not
# be available, so we need to be able to fall back to a fake implementation in that case as well.


SCREENSAVER_BUS = "org.freedesktop.ScreenSaver"
SCREENSAVER_PATH = "/org/freedesktop/ScreenSaver"


class FakeMessageBus:

    def __init__(self):
        self._connected = False

    async def connect(self):
        self._connected = True
        logger.debug("Connect to fake D-Bus")
        return self

    def disconnect(self):
        logger.debug("Disconnect from fake D-Bus")
        self._connected = False

    async def wait_for_disconnect(self):
        while self._connected:
            await asyncio.sleep(0)
        logger.debug("Disconnected from fake D-Bus")

    async def introspect(self, name, path):
        assert name == SCREENSAVER_BUS
        assert path == SCREENSAVER_PATH
        return dict(name=name, path=path)

    def get_proxy_object(self, name, path, introspection):
        assert introspection["name"] == name
        assert introspection["path"] == path
        return FakeBusProxy(introspection)


class FakeBusProxy:

    def __init__(self, introspection):
        self.introspection = introspection

    def get_interface(self, name):
        assert self.introspection["name"] == name
        return FakeScreenSaver()


class FakeScreenSaver:

    _next_cookie = 1

    _extant_cookies = set()

    async def call_inhibit(self, app_name, reason):
        cookie = FakeScreenSaver._next_cookie
        FakeScreenSaver._extant_cookies.add(cookie)
        FakeScreenSaver._next_cookie += 1
        logger.debug("Fake ScreenSaver Inhibit gives cookie %r", cookie)
        return cookie

    async def call_un_inhibit(self, cookie):
        FakeScreenSaver._extant_cookies.remove(cookie)
        logger.debug("Fake ScreenSaver UnInhibit: cookie %r", cookie)

    async def call_simulate_user_activity(self):
        logger.debug("Fake ScreenSaver SimulateUserActivity")


def _make_bus():
    try:
        return MessageBus()
    except Exception:
        return FakeMessageBus()


@asynccontextmanager
async def _bus():
    bus = await _make_bus().connect()
    try:
        yield bus
    finally:
        bus.disconnect()
        await bus.wait_for_disconnect()
        pass

async def screensaver(bus):
    try:
        introspection = await bus.introspect(
            SCREENSAVER_BUS,
            SCREENSAVER_PATH,
        )
        obj = bus.get_proxy_object(
            SCREENSAVER_BUS,
            SCREENSAVER_PATH,
            introspection,
        )
        return obj.get_interface(SCREENSAVER_BUS)
    except (
        InvalidBusNameError,
        InvalidObjectPathError,
        InvalidInterfaceNameError,
        InvalidMemberNameError,
    ):
        # The required endpoints for the screensaver aren't available
        return FakeScreenSaver()


async def _inhibit(bus, reason: str, app_name: Optional[str]=None) -> int:
    if app_name is None:
        app_name = sys.argv[0]
    s = await screensaver(bus)
    cookie = await s.call_inhibit(app_name, reason)
    logger.debug("ScreenSaver Inhibit: %r gives cookie %r", reason, cookie)
    return cookie


async def _uninhibit(bus, cookie: int):
    s = await screensaver(bus)
    await s.call_un_inhibit(cookie)
    logger.debug("ScreenSaver UnInhibit: cookie %r", cookie)


async def _simulate_user_activity(bus):
    s = await screensaver(bus)
    await s.call_simulate_user_activity()
    logger.debug("ScreenSaver SimulateUserActivity")


async def _inhibited_screensaver(
    reason: str,
    app_name: Optional[str],
    on_inhibited: threading.Event,
    on_uninhibit: threading.Event,
    on_error: threading.Event,
    wake: bool=True,
):
    try:
        async with _bus() as bus:
            cookie = await _inhibit(bus, reason, app_name)

            if wake:
                await _simulate_user_activity(bus)

            on_inhibited.set()

            while not on_uninhibit.is_set():
                await asyncio.sleep(0)

            await _uninhibit(bus, cookie)
    except:
        # If an error occurs, tell the parent thread to stop waiting
        on_error.set()
        raise


@contextmanager
def inhibited_screensaver(reason: str, *, app_name: Optional[str]=None, wake: bool=True):
    """A context manager to inhibit the screensaver.

    Args:
        reason: A descriptive reason for inhibiting the screensaver.

        app_name: The name of the application inhibiting the screensaver. Defaults to the
            name of the current executable.

        wake: Whether to simulate user activity to wake the display. Defaults to True.

    Raises:
        Exception: If an error occurs while inhibiting the screensaver.
    """
    on_inhibited = threading.Event()
    on_uninhibit = threading.Event()
    on_error = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        coro = _inhibited_screensaver(reason, app_name, on_inhibited, on_uninhibit, on_error, wake)
        future = pool.submit(asyncio.run, coro)

        # Wait for on_inhibited, but accept that an error may have happened
        while not on_inhibited.is_set():
            if on_error.is_set():
                future.result(timeout=5.0)  # Should raise
            time.sleep(0)

        try:
            yield
        finally:
            on_uninhibit.set()
            future.result(timeout=5.0) # Raises if an error occurred
