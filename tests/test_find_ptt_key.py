"""Tests for scripts/find_ptt_key.py — filter_key_devices.

These tests verify device filtering logic without needing real evdev
devices or root/input-group permissions.
"""
import importlib.util
import os
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def find_module(mock_gpu_modules):
    """Import find_ptt_key.py with evdev available (real or stubbed)."""
    script_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "find_ptt_key.py"
    )
    spec = importlib.util.spec_from_file_location("find_module", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_mock_device(has_evkey=True, raises=None):
    """Create a mock InputDevice with configurable capabilities."""
    dev = MagicMock()
    dev.path = "/dev/input/event99"
    dev.name = "Mock Device"

    if raises:
        dev.capabilities.side_effect = raises
    elif has_evkey:
        dev.capabilities.return_value = {1: [102]}  # EV_KEY: KEY_RIGHTCTRL
    else:
        dev.capabilities.return_value = {0: [0]}  # No EV_KEY

    return dev


class TestFilterKeyDevices:

    def test_includes_device_with_evkey(self, find_module):
        """A device with EV_KEY capabilities should be included."""
        dev = make_mock_device(has_evkey=True)
        devices = [("/dev/input/event0", dev)]

        result = find_module.filter_key_devices(devices)

        assert len(result) == 1
        assert result[0][0] == "/dev/input/event0"

    def test_excludes_device_without_evkey(self, find_module):
        """A device without EV_KEY capabilities should be excluded."""
        dev = make_mock_device(has_evkey=False)
        devices = [("/dev/input/event0", dev)]

        result = find_module.filter_key_devices(devices)

        assert result == []

    def test_skips_permission_error(self, find_module):
        """Devices that raise PermissionError should be silently skipped."""
        dev = make_mock_device(raises=PermissionError("access denied"))
        devices = [("/dev/input/event0", dev)]

        result = find_module.filter_key_devices(devices)

        assert result == []

    def test_skips_oserror(self, find_module):
        """Devices that raise OSError should be silently skipped."""
        dev = make_mock_device(raises=OSError("device gone"))
        devices = [("/dev/input/event0", dev)]

        result = find_module.filter_key_devices(devices)

        assert result == []

    def test_mixed_devices(self, find_module):
        """A mix of valid, invalid, and error-raising devices should
        return only the valid ones."""
        good_dev = make_mock_device(has_evkey=True)
        good_dev.name = "Good Keyboard"
        no_key_dev = make_mock_device(has_evkey=False)
        perm_dev = make_mock_device(raises=PermissionError())

        devices = [
            ("/dev/input/event3", good_dev),
            ("/dev/input/event4", no_key_dev),
            ("/dev/input/event5", perm_dev),
            ("/dev/input/event6", good_dev),
        ]

        result = find_module.filter_key_devices(devices)

        assert len(result) == 2
        assert result[0][0] == "/dev/input/event3"
        assert result[1][0] == "/dev/input/event6"

    def test_empty_input(self, find_module):
        """An empty device list should return an empty list."""
        assert find_module.filter_key_devices([]) == []

    def test_preserves_device_objects(self, find_module):
        """The returned tuples should contain the original device objects."""
        dev = make_mock_device(has_evkey=True)
        devices = [("/dev/input/event0", dev)]

        result = find_module.filter_key_devices(devices)

        assert result[0][1] is dev
