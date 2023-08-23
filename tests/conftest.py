import os
import asyncio
import platform
from unittest.mock import Mock, patch

from pytest import fixture


# It's very difficult to run DBus in some test environments so if
# We're on Linux and DBus doesn't seem to be available, we patch our
# Linux driver to use the Mock DBus interfaces defined below.

is_linux = platform.system().lower().startswith("linux")

dbus_available = bool(os.environ.get("DBUS_SESSION_BUS_ADDRESS", None))


class MockDBus:

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
        return dict(name=name, path=path)

    def get_proxy_object(self, name, path, introspection):
        assert introspection["name"] == name
        assert introspection["path"] == path
        return MockDBusProxy(introspection)
    

class MockDBusProxy:

    def __init__(self, introspection):
        self.introspection = introspection

    def get_interface(self, name):
        assert self.introspection["name"] == name
        return MockScreenSaver()
    

class MockScreenSaver:

    _next_cookie = 1

    _extant_cookies = set()

    async def call_inhibit(self, app_name, reason):
        cookie = MockScreenSaver._next_cookie
        MockScreenSaver._extant_cookies.add(cookie)
        MockScreenSaver._next_cookie += 1
        return cookie
    
    async def call_un_inhibit(self, cookie):
        MockScreenSaver._extant_cookies.remove(cookie)



@fixture(autouse=is_linux and not dbus_available, scope="function")
def mock_dbus():
    with patch("eugeroic.drivers.linux.bus.MessageBus", new=MockDBus):
        yield
