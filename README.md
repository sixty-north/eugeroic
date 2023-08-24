# Eugeroic

Tools in Python for keeping a computer display awake.

eugeroic
:  (_adjective_) keeping one awake. Of a wakefulness promoting agent.


Sometimes you need to perform a task without the screensaver kicking in, or the display being
suspended entirely. This may be because you are capturing the screen, or because you are running
presentation software, or because you are running a long-running task that you want to monitor
without interaction. This module provides a context manager and a decorator that can be used to
keep the display awake while the block or function is running.

## Installation

    $ pip install eugeroic


## Examples

The `wakefulness` context manager keeps the computer awake while the block is running:

    # Keep the computer awake while capturing the screen.

    from eugeroic import wakefulness
    
    with wakefulness("Capture the screen"):
        capture_screen(seconds=500)


The `stay_awake` decorator keeps the computer awake while the decorated function is running:

    # Keep the computer awake while capturing the screen.

    from eugeroic import stay_awake
    
    @stay_awake("Capture the screen")
    def capture_screen(seconds):
        ...


How it works
============

On Windows calls to `SetThreadExecutionState` are used.

On macOS IOKit Power Management functions are used.

On Linux, an attempt is made to communicate with the desktop environment through D-Bus messages.

Note that while every attempt is made to keep the computer and display awake, there is no guarantee
that the display will not be suspended. For example, on macOS, the display will be suspended if the
user locks the screen. On Linux, the display will be suspended if the user switches to a different
virtual terminal. On Windows, the display will be suspended if the user locks the screen or switches
to a different user account.  In particular, on Linux, there is no guarantee that the required D-Bus
messages will be handled by the desktop environment.  In practice though, _Eugeroic_ usually works.
