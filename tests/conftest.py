import platform
import subprocess

from pytest import fixture


is_linux = platform.system.lower().startswith("linux")


@fixture(autouse=is_linux, scope="session")
def dbus():
    """Start a D-Bus daemon."""
    dbus_launch = subprocess.run(
        ["dbus-launch", "--sh-syntax"]
        capture_output=True,
        check=True,
    )
    print("stdout = ", dbus_launch.stdout)
    