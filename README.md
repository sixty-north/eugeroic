# Eugeroic

Tools for keeping a computer awake.

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
