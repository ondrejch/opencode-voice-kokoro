#!/usr/bin/env python3
"""
Find the evdev device path and key code for a push-to-talk key.

Prints a numbered list of input devices, then watches all of them
for key events.  Press the key you want to use for PTT and the
output tells you exactly what to put in voice.py.

This script does not grab the devices, so your keyboard keeps working
normally while it runs.

Usage:
    python find_ptt_key.py

Requires:
    pip install evdev
    sudo usermod -aG input "$USER"  (then log out/in)
"""

import sys
import select

from evdev import InputDevice, ecodes, list_devices


def filter_key_devices(devices):
    """Given an iterable of (path, InputDevice) pairs, return only those
    that support EV_KEY events.  Devices that raise PermissionError or
    OSError when queried are silently skipped.
    """
    result = []

    for path, dev in devices:
        try:
            caps = dev.capabilities()
            if ecodes.EV_KEY in caps:
                result.append((path, dev))
        except PermissionError:
            continue
        except OSError:
            continue

    return result


def main():
    devices = filter_key_devices(
        (path, InputDevice(path)) for path in list_devices()
    )

    if not devices:
        print("No input devices found.  Are you in the 'input' group?")
        print("  sudo usermod -aG input \"$USER\"")
        sys.exit(1)

    print("Input devices with keys:\n")
    for i, (path, dev) in enumerate(devices):
        marker = "  <-- has keys"
        print(f"  [{i}] {path}  {dev.name}{marker}")
    print()
    print("Press the key you want to use for push-to-talk.")
    print("Press Ctrl+C to quit.\n")

    try:
        while True:
            ready, _, _ = select.select([dev for _, dev in devices], [], [])

            for dev in ready:
                for event in dev.read():
                    if event.type != ecodes.EV_KEY or event.value != 1:
                        continue

                    code_name = ecodes.KEY.get(event.code, f"0x{event.code:04x}")

                    print(f"\nDevice: {dev.path}  {dev.name}")
                    print(f"  PTT_PATH = \"{dev.path}\"")
                    print(f"  PTT_KEY  = ecodes.{code_name}")
                    print(f"  # or numerically: PTT_KEY = {event.code}")
                    print()

    except KeyboardInterrupt:
        print("\nDone.")


if __name__ == "__main__":
    main()
