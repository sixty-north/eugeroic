import ctypes
import time


# https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED= 0x00000002

MOUSEEVENTF_MOVE = 0x0001

def inhibit_screensaver():
    """Inhibit the screensaver from starting."""
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS| ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )

def uninhibit_screensaver():
    """Uninhibit the screensaver from starting."""
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)


def simulate_user_activity():
    """Simulate user activity with a mouse move event."""
    # A single move event with a delta of (0, 0) is enough to wake the display
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, 0, 0, 0, 0)
