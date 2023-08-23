from contextlib import asynccontextmanager, contextmanager
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


SCREENSAVER_BUS = "org.freedesktop.ScreenSaver"
SCREENSAVER_PATH = "/org/freedesktop/ScreenSaver"


class FakeMessageBus:
    
    def __init__(self):
        self._connected = False

    async def connect(self):
        self._connected = True
        return self       

    def disconnect(self):
        self._connected = False
    
    async def wait_for_disconnect(self):
        while self._connected:
            await asyncio.sleep(0)

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
        return cookie
    
    async def call_un_inhibit(self, cookie):
        FakeScreenSaver._extant_cookies.remove(cookie)



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
        # The required endpoints for the screensave aren't available
        return FakeScreenSaver()
        


async def _inhibit(bus, reason: str, app_name: Optional[str]=None) -> int:
    if app_name is None:
        app_name = sys.argv[0]
    s = await screensaver(bus)
    cookie = await s.call_inhibit(app_name, reason)
    return cookie


async def _uninhibit(bus, cookie: int):
    s = await screensaver(bus)
    await s.call_un_inhibit(cookie)


async def _inhibited_screensaver(
    reason: str,
    app_name: Optional[str],
    on_inhibited: threading.Event,
    on_uninhibit: threading.Event,
    on_error: threading.Event,
):
    try:
        async with _bus() as bus:
            cookie = await _inhibit(bus, reason, app_name)
            on_inhibited.set()

            while not on_uninhibit.is_set():
                await asyncio.sleep(0)

            await _uninhibit(bus, cookie)
    except:
        # If an error occurs, tell the parent thread to stop waiting
        on_error.set()  
        raise


@contextmanager
def inhibited_screensaver(reason: str, app_name: Optional[str]=None):
    on_inhibited = threading.Event()
    on_uninhibit = threading.Event()
    on_error = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        coro = _inhibited_screensaver(reason, app_name, on_inhibited, on_uninhibit, on_error)
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
