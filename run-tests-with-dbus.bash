#!/usr/bin/env bash
if test -z "$DBUS_SESSION_BUS_ADDRESS" ; then
    echo "Starting dbus" 
    eval `dbus-launch --sh-syntax`
    echo "D-Bus per-session daemon address is: $DBUS_SESSION_BUS_ADDRESS"
fi
python -m pytest tests/
