"""
Shared fixtures for voice-related tests.

The scripts (voice.py, tts_server.py) import heavy GPU-only modules
at the top level: faster_whisper, torch, kokoro, sounddevice.  These
are unavailable in a CI or test environment without CUDA.

We inject MagicMock replacements into sys.modules BEFORE importing
the scripts, so their module-level code runs without needing a GPU.
"""
import sys
import types
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_gpu_modules():
    """Replace heavy GPU modules with MagicMock so scripts can be imported."""
    heavy = [
        "faster_whisper",
        "torch",
        "kokoro",
        "sounddevice",
        "soundfile",
        "numpy",
    ]

    originals = {}
    for mod_name in heavy:
        originals[mod_name] = sys.modules.get(mod_name)
        sys.modules[mod_name] = MagicMock()

    # evdev must remain real — it's lightweight and needed for ecodes constants
    # but we need to ensure it's importable even if not installed.
    if "evdev" not in sys.modules:
        try:
            import evdev  # noqa: F401
        except ImportError:
            # Create a minimal stub with the constants we need
            evdev_stub = types.ModuleType("evdev")
            ecodes_stub = types.ModuleType("evdev.ecodes")

            # Minimal key code mapping
            ecodes_stub.EV_KEY = 1
            ecodes_stub.KEY_RIGHTCTRL = 102
            ecodes_stub.KEY_HOMEPAGE = 172
            ecodes_stub.KEY = {
                102: "KEY_RIGHTCTRL",
                172: "KEY_HOMEPAGE",
            }

            evdev_stub.ecodes = ecodes_stub
            evdev_stub.InputDevice = MagicMock()
            evdev_stub.list_devices = MagicMock(return_value=[])

            sys.modules["evdev"] = evdev_stub
            sys.modules["evdev.ecodes"] = ecodes_stub

    yield

    # Restore originals
    for mod_name, original in originals.items():
        if original is None:
            sys.modules.pop(mod_name, None)
        else:
            sys.modules[mod_name] = original
