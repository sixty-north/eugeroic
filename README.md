# Eugeroic

Tools for keeping a computer awake.

## Installation

    $ pip install eugeroic


## Examples

    # Keep the computer awake while capturing the screen.

    from eugeroic import wakefulness
    
    with wakefulness("Capture the screen"):
        capture_screen(seconds=500)
