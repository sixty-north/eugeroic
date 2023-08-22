import contextlib
import ctypes.util
import time
from enum import IntEnum

try:
    from enum import StrEnum  # Introduced in Python 3.11
except ImportError:
    from backports.strenum import StrEnum

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

    iokit.IOPMAssertionDeclareUserActivity.argtypes = [
        ctypes.c_void_p,                 # CFStringRef
        ctypes.c_uint32,                 # IOPMUserActiveType
        ctypes.POINTER(ctypes.c_uint32)  # IOPMAssertionID
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


class UserActiveType(IntEnum):
    """IOPMUserActiveType"""
    Local = 0
    Remote = 1


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


def assertion_declare_user_activity(iokit, assertion_name: str, user_active_type: UserActiveType):
    assertion_id = ctypes.c_uint32()
    status = iokit.IOPMAssertionDeclareUserActivity(
        cfstringref(assertion_name),
        user_active_type,
        ctypes.byref(assertion_id)
    )
    if status != 0:
        raise RuntimeError(f"Failed to declare user activity: {assertion_name!r}")
    return assertion_id


@contextlib.contextmanager
def power_management_assertion(assertion_type: AssertionType, level, reason):
    iokit = get_iokit()
    assertion_id = assertion_create_name(iokit, assertion_type, level, reason)
    try:
        yield
    finally:
        assertion_release(iokit, assertion_id)


def declare_local_user_activity(reason):
    """Declare local activity to wake the screen."""
    iokit = get_iokit()
    assertion_declare_user_activity(iokit, reason, UserActiveType.Local)
    print("Declared local user activity.")


def main():
    declare_local_user_activity("Wake up!")
    with power_management_assertion(AssertionType.NoDisplaySleep, Level.On, "Busy busy busy..."):
        for i in range(600):
            print(i)
            time.sleep(1)


if __name__ == '__main__':
    main()