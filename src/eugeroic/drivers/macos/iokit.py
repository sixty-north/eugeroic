import contextlib
import ctypes.util
import time
from enum import IntEnum, StrEnum

from eugeroic.drivers.macos.cfstringref import cfstringref

_iokit = None


def get_iokit():
    global _iokit
    if _iokit is None:
        _iokit = load_iokit()
    return _iokit


def load_iokit():
    iokit = ctypes.cdll.LoadLibrary(ctypes.util.find_library('IOKit'))

    iokit.IOPMAssertionCreateWithName.argtypes = [
        ctypes.c_void_p,                 # CFStringRef
        ctypes.c_uint32,                 # IOPMAssertionLevel
        ctypes.c_void_p,                 # CFStringRef
        ctypes.POINTER(ctypes.c_uint32)  # IOPMAssertionID
    ]

    iokit.IOPMAssertionRelease.argtypes = [
        ctypes.c_uint32  # IOPMAssertionID
    ]
    return iokit


class Level(IntEnum):
    """IOPMAssertionLevel"""
    Off = 0
    On = 255


class AssertionType(StrEnum):
    """IOPMAssertionType"""
    PreventUserIdleSystemSleep = "PreventUserIdleSystemSleep"
    PreventUserIdleDisplaySleep = "PreventUserIdleDisplaySleep"
    PreventSystemSleep = "PreventSystemSleep"
    NoIdleSleep = "NoIdleSleepAssertion"
    NoDisplaySleep = "NoDisplaySleepAssertion"


def assertion_create_name(iokit, assertion_type: str, level: Level, reason: str):
    assertion_id = ctypes.c_uint32()
    status = iokit.IOPMAssertionCreateWithName(
        cfstringref(assertion_type),
        level,
        cfstringref(reason),
        ctypes.byref(assertion_id)
    )
    if status != 0:
        raise RuntimeError(f"Failed to create assertion with name: {assertion_type!r}")
    return assertion_id


def assertion_release(iokit, assertion_id: int):
    status = iokit.IOPMAssertionRelease(assertion_id)
    if status != 0:
        raise RuntimeError(f"Failed to release assertion: {assertion_id}")


@contextlib.contextmanager
def power_management_assertion(assertion_type: AssertionType, level, reason):
    iokit = get_iokit()
    assertion_id = assertion_create_name(iokit, assertion_type, level, reason)
    try:
        yield
    finally:
        assertion_release(iokit, assertion_id)


def main():
    with power_management_assertion(AssertionType.NoDisplaySleep, Level.On, "Busy busy busy..."):
        for i in range(600):
            print(i)
            time.sleep(1)


if __name__ == '__main__':
    main()