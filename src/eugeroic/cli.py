"""A simple command-line interface for the eugeroic package.

Keep the display away for a given number of seconds.

Example:
    $ python -m eugeroic 60
"""

import argparse
import sys
import time

from eugeroic import wakefulness


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seconds", type=int, help="number of seconds to keep the display awake")
    parser.add_argument("--reason", default="eugeroic", help="reason for keeping the display awake")
    args = parser.parse_args(argv)
    with wakefulness(args.reason):
        time.sleep(args.seconds)


if __name__ == "__main__":
    sys.exit(main())