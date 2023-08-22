# In order to use dbus-python on Debian 12, I had to,
# sudo apt install libdbus-glib-1-2 libdbus-glib-1-dev
# pip install dbus-python

import sys
import contextlib
from typing import Optional

import dbus


_bus = None

def bus():
    global _bus
    if _bus is None:
        _bus = dbus.SessionBus()
    return dbus.SessionBus()


_interface = None

def screensaver():
    global _interface
    if _interface is None:
        proxy = bus().get_object("org.freedesktop.ScreenSaver", "/org/freedesktop/ScreenSaver")
        _interface = dbus.Interface(proxy, 'org.freedesktop.ScreenSaver')
    return _interface


def inhibit(reason: str, app_name: Optional[str]=None) -> int:
    """Inhibit the screensaver.
    
    Args:
        reason: A description of the reason.
        app_name: An optional app name. If not given the process name will be used.

    Returns:
        A cookie used to unqiuely identify this request, to be passed to uninhibit() when done.
    """
    if app_name is None:
        app_name = sys.argv[0]
    cookie = screensaver().Inhibit(app_name, reason)
    return cookie

def uninhibit(cookie: int):
    screensaver().UnInhibit(cookie)


@contextlib.contextmanager
def inhibited_screensaver(reason: str, app_name: Optional[str]=None):
    cookie = inhibit(reason, app_name)
    try:
        yield
    finally:
        uninhibit(cookie)
