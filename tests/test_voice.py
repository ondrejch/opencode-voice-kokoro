"""Tests for scripts/voice.py — stop_tts, type_into_opencode, audio_callback.

These tests run without a GPU or microphone.  Heavy modules
(faster_whisper, torch, sounddevice, numpy) are mocked via conftest.py.
"""
import importlib.util
import os
import signal
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def voice_module(mock_gpu_modules):
    """Import voice.py fresh for each test, with GPU modules mocked."""
    script_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "voice.py"
    )
    spec = importlib.util.spec_from_file_location("voice_module", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- stop_tts ---

class TestStopTts:

    def test_no_pid_file(self, voice_module, tmp_path):
        """stop_tts should not crash when the PID file doesn't exist."""
        with patch.object(voice_module, "TTS_PID_FILE", str(tmp_path / "nonexistent.pid")):
            voice_module.stop_tts()  # should not raise

    def test_invalid_pid_content(self, voice_module, tmp_path):
        """stop_tts should not crash when the PID file has non-numeric content."""
        pid_file = tmp_path / "tts.pid"
        pid_file.write_text("not a number\n")

        with patch.object(voice_module, "TTS_PID_FILE", str(pid_file)):
            voice_module.stop_tts()  # should not raise

    def test_empty_pid_file(self, voice_module, tmp_path):
        """stop_tts should not crash when the PID file is empty."""
        pid_file = tmp_path / "tts.pid"
        pid_file.write_text("")

        with patch.object(voice_module, "TTS_PID_FILE", str(pid_file)):
            voice_module.stop_tts()

    def test_dead_pid(self, voice_module, tmp_path):
        """stop_tts should not crash when the PID refers to a dead process."""
        pid_file = tmp_path / "tts.pid"
        pid_file.write_text("99999999\n")

        with patch.object(voice_module, "TTS_PID_FILE", str(pid_file)):
            with patch("os.kill", side_effect=ProcessLookupError):
                voice_module.stop_tts()

    def test_valid_pid_sends_sigusr1(self, voice_module, tmp_path):
        """stop_tts should send SIGUSR1 to the PID in the file."""
        pid_file = tmp_path / "tts.pid"
        pid_file.write_text("12345\n")

        with patch.object(voice_module, "TTS_PID_FILE", str(pid_file)):
            with patch("os.kill") as mock_kill:
                voice_module.stop_tts()

                mock_kill.assert_called_once_with(12345, signal.SIGUSR1)


# --- type_into_opencode ---

class TestTypeIntoOpencode:

    def test_wayland_uses_wtype(self, voice_module):
        """On Wayland, wtype should be called first."""
        with patch.dict(os.environ, {
            "XDG_SESSION_TYPE": "wayland",
            "WAYLAND_DISPLAY": "wayland-0",
        }):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)

                voice_module.type_into_opencode("hello world")

                first_call = mock_run.call_args_list[0]
                assert first_call.args[0] == ["wtype", "--", "hello world"]

    def test_x11_uses_xdotool(self, voice_module):
        """On X11, xdotool should be called."""
        with patch.dict(os.environ, {
            "XDG_SESSION_TYPE": "x11",
        }, clear=True):
            with patch("subprocess.run") as mock_run:
                voice_module.type_into_opencode("hello world")

                args = mock_run.call_args_list[0].args[0]
                assert args[0] == "xdotool"
                assert "type" in args
                assert "--clearmodifiers" in args

    def test_no_session_uses_xdotool(self, voice_module):
        """With no session type set, xdotool fallback should be used."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("subprocess.run") as mock_run:
                voice_module.type_into_opencode("test")

                args = mock_run.call_args_list[0].args[0]
                assert args[0] == "xdotool"

    def test_wayland_wtype_fails_falls_back_to_xdotool(self, voice_module):
        """If wtype fails on Wayland, xdotool should be tried as fallback."""
        with patch.dict(os.environ, {
            "XDG_SESSION_TYPE": "wayland",
            "WAYLAND_DISPLAY": "wayland-0",
        }):
            with patch("subprocess.run") as mock_run:
                # First call (wtype) fails, second (xdotool) succeeds
                mock_run.side_effect = [
                    MagicMock(returncode=1),
                    MagicMock(returncode=0),
                ]

                voice_module.type_into_opencode("hello")

                assert mock_run.call_count == 2
                assert mock_run.call_args_list[0].args[0] == ["wtype", "--", "hello"]
                assert mock_run.call_args_list[1].args[0][0] == "xdotool"

    def test_wayland_without_display_uses_xdotool(self, voice_module):
        """Wayland session but no WAYLAND_DISPLAY should fall back to xdotool."""
        with patch.dict(os.environ, {
            "XDG_SESSION_TYPE": "wayland",
        }, clear=True):
            with patch("subprocess.run") as mock_run:
                voice_module.type_into_opencode("test")

                args = mock_run.call_args_list[0].args[0]
                assert args[0] == "xdotool"


# --- audio_callback ---

class TestAudioCallback:

    def test_not_recording_does_not_append(self, voice_module):
        """When not recording, audio_callback should not append frames."""
        voice_module.recording = False
        voice_module.frames = []

        indata = MagicMock()
        voice_module.audio_callback(indata, 1024, None, None)

        assert voice_module.frames == []

    def test_recording_appends_frames(self, voice_module):
        """When recording, audio_callback should append a copy of indata."""
        voice_module.recording = True
        voice_module.frames = []

        indata = MagicMock()
        indata.copy = MagicMock(return_value="copied_data")

        voice_module.audio_callback(indata, 1024, None, None)

        assert voice_module.frames == ["copied_data"]

    def test_status_prints(self, voice_module, capsys):
        """When status is non-None, audio_callback should print it."""
        voice_module.recording = False
        voice_module.audio_callback(MagicMock(), 1024, None, "overflow")

        captured = capsys.readouterr()
        assert "overflow" in captured.out
