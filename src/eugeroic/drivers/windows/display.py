import ctypes

# https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED= 0x00000002

def inhibit_screensaver():
    """Inhibit the screensaver from starting."""
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS| ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )

def uninhibit_screensaver():
    """Uninhibit the screensaver from starting."""
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
