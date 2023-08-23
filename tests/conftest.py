import os
import platform
import subprocess

from pytest import fixture


is_linux = platform.system().lower().startswith("linux")

@fixture(autouse=is_linux, scope="session")
def dbus():
    """Start a D-Bus daemon."""
    if "DBUS_SESSION_BUS_ADDRESS" not in os.environ:
        dbus_launch = subprocess.run(
            ["dbus-launch", "--sh-syntax", "--exit-with-x11"],
            capture_output=True,
            check=True,
        )
        output = dbus_launch.stdout.decode()
        lines = output.splitlines()
        for line in lines:
            variable, equals, value = line.strip(";").partition("=")
            if equals == "=":
                value = value.strip("'")
                os.environ[variable] = value
    