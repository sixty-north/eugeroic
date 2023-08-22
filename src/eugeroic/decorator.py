import functools
import inspect

from eugeroic import wakefulness


def stay_awake(arg=None, reason: str | None=None):
    """A decorator to prevent the display from sleeping.

    The display will be kept awake for the duration of the decorated function.

    This decorator may be used with or without arguments.

    Args:
        f: The function to decorate.

        reason: An descriptive reason for keeping the display awake. If not provided the
            first line of the docstring of the decorated function will be used, or if not
            available the name of the decorated function will be used.
    """

    if (not callable(arg)) and isinstance(arg, str):
        if  reason is None:
            return functools.partial(stay_awake, reason=arg)
        else:
            raise TypeError(
                "Cannot specify 'reason' as both a positional argument and "
                "a keyword argument to stay_awake."
            )
    elif arg is None:
        return functools.partial(stay_awake, reason=reason)
    else:
        f = arg

    if reason is None:
        docstring = inspect.getdoc(f)
        docstring = docstring and docstring.splitlines()[0].strip()
        reason = docstring or f.__name__

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with wakefulness(reason):
            return f(*args, **kwargs)

    return wrapper
