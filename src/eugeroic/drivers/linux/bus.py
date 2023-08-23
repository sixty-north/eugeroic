from contextlib import asynccontextmanager, contextmanager
import sys
import asyncio
import concurrent.futures
from typing import Optional

from dbus_next.aio import MessageBus


SCREENSAVER_BUS = "org.freedesktop.ScreenSaver"
SCREENSAVER_PATH = "/org/freedesktop/ScreenSaver"


@asynccontextmanager
async def _bus():
    bus = await MessageBus().connect()
    try:
        yield bus
    finally:
        bus.wait_for_disconnect()


async def screensaver(bus):
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


async def _inhibit(bus, reason: str, app_name: Optional[str]=None) -> int:
    if app_name is None:
        app_name = sys.argv[0]
    s = await screensaver(bus)
    cookie = await s.call_inhibit(app_name, reason)
    return cookie


async def _uninhibit(bus, cookie: int):
    s = await screensaver(bus)
    await s.call_un_inhibit(cookie)


async def _ainhibit(reason: str, app_name: Optional[str]=None) -> int:
    async with _bus() as bus:
        return await _inhibit(bus, reason, app_name)


async def _auninhibit(cookie: int):
    async with _bus() as bus:
        return await _uninhibit(bus, cookie)


def _synchronize(coro):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()    


def inhibit(reason: str, app_name: Optional[str]=None) -> int:
    return _synchronize(_ainhibit(reason, app_name))


def uninhibit(cookie: int):
    return _synchronize(_auninhibit(cookie))


@contextmanager
def inhibited_screensaver(reason: str, app_name: Optional[str]=None):
    cookie = inhibit(reason, app_name)
    try:
        yield
    finally:
        uninhibit(cookie)
