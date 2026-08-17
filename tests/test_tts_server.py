"""Tests for scripts/tts_server.py — cleanup, request_stop, run_server.

These tests run without a GPU.  Heavy modules (torch, kokoro,
sounddevice) are mocked via conftest.py.
"""
import importlib.util
import os
import threading
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def tts_module(mock_gpu_modules):
    """Import tts_server.py with GPU modules mocked.

    Import is safe — execution code (model loading, socket bind,
    accept loop) is guarded by `if __name__ == "__main__":`.
    """
    script_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "tts_server.py"
    )
    spec = importlib.util.spec_from_file_location("tts_module", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- device backend ---

class TestTtsDevice:

    def test_default_device_is_cuda_or_cpu(self, tts_module):
        assert tts_module.TTS_DEVICE in ("cuda", "cpu")

    def test_cpu_env(self, mock_gpu_modules, monkeypatch):
        monkeypatch.setenv("OPENCODE_TTS_DEVICE", "cpu")
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "scripts", "tts_server.py"
        )
        spec = importlib.util.spec_from_file_location("tts_cpu", script_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert mod.TTS_DEVICE == "cpu"

    def test_invalid_device_exits(self, mock_gpu_modules, monkeypatch):
        monkeypatch.setenv("OPENCODE_TTS_DEVICE", "metal")
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "scripts", "tts_server.py"
        )
        spec = importlib.util.spec_from_file_location("tts_bad", script_path)
        mod = importlib.util.module_from_spec(spec)
        with pytest.raises(SystemExit):
            spec.loader.exec_module(mod)

    def test_run_server_places_model_on_configured_device(
        self, tts_module, tmp_path
    ):
        """KModel().to(TTS_DEVICE) should use the configured backend."""
        tts_module.TTS_DEVICE = "cpu"
        pid_path = tmp_path / "tts.pid"
        socket_path = tmp_path / "tts.sock"

        mock_server = MagicMock()
        mock_server.accept.side_effect = KeyboardInterrupt
        mock_model_instance = MagicMock()
        tts_module.KModel.return_value = mock_model_instance
        mock_model_instance.to.return_value = mock_model_instance
        mock_model_instance.eval.return_value = mock_model_instance

        with patch.object(tts_module, "PID_FILE", str(pid_path)):
            with patch.object(tts_module, "SOCKET", str(socket_path)):
                with patch.object(
                    tts_module.socket, "socket", return_value=mock_server
                ):
                    try:
                        tts_module.run_server()
                    except KeyboardInterrupt:
                        pass

        mock_model_instance.to.assert_called_with("cpu")


# --- cleanup ---

class TestCleanup:

    def test_removes_socket_and_pid(self, tts_module, tmp_path):
        """cleanup should remove socket and PID files if they belong to this process."""
        socket_path = tmp_path / "tts.sock"
        pid_path = tmp_path / "tts.pid"
        socket_path.touch()
        pid_path.write_text(str(os.getpid()))

        with patch.object(tts_module, "SOCKET", str(socket_path)):
            with patch.object(tts_module, "PID_FILE", str(pid_path)):
                tts_module.cleanup()

                assert not socket_path.exists()
                assert not pid_path.exists()

    def test_does_not_remove_foreign_socket(self, tts_module, tmp_path):
        """cleanup should not remove a socket owned by another process."""
        socket_path = tmp_path / "tts.sock"
        pid_path = tmp_path / "tts.pid"
        socket_path.touch()
        pid_path.write_text("99999")  # foreign PID

        with patch.object(tts_module, "SOCKET", str(socket_path)):
            with patch.object(tts_module, "PID_FILE", str(pid_path)):
                tts_module.cleanup()

                assert socket_path.exists()  # should not be removed

    def test_no_files_no_error(self, tts_module, tmp_path):
        """cleanup should not error if files don't exist."""
        socket_path = tmp_path / "nonexistent.sock"
        pid_path = tmp_path / "nonexistent.pid"

        with patch.object(tts_module, "SOCKET", str(socket_path)):
            with patch.object(tts_module, "PID_FILE", str(pid_path)):
                tts_module.cleanup()  # should not raise


# --- request_stop ---

class TestRequestStop:

    def test_sets_stop_event(self, tts_module):
        """request_stop should set the stop_requested event."""
        tts_module.stop_requested.clear()
        assert not tts_module.stop_requested.is_set()

        tts_module.request_stop()

        assert tts_module.stop_requested.is_set()

    def test_stop_calls_sd_stop(self, tts_module):
        """request_stop should call sd.stop() to halt playback."""
        tts_module.request_stop()

        tts_module.sd.stop.assert_called()

    def test_stop_catches_sd_errors(self, tts_module):
        """request_stop should not raise even if sd.stop() fails."""
        tts_module.sd.stop.side_effect = RuntimeError("device gone")

        tts_module.request_stop()  # should not raise


# --- stop_requested event ---

class TestStopRequestedEvent:

    def test_event_is_threading_event(self, tts_module):
        """stop_requested should be a threading.Event instance."""
        assert isinstance(tts_module.stop_requested, threading.Event)


# --- speak (integration with mocked pipeline) ---

class TestSpeak:

    def test_speak_clears_stop_flag_at_start(self, tts_module):
        """speak() should clear stop_requested at the beginning."""
        tts_module.stop_requested.set()

        # Mock pipeline to yield nothing so the loop body doesn't run
        tts_module.pipeline = MagicMock(return_value=iter([]))

        tts_module.speak("test")

        assert not tts_module.stop_requested.is_set()

    def test_speak_with_empty_pipeline_does_not_crash(self, tts_module):
        """speak() should handle an empty pipeline result without error."""
        tts_module.pipeline = MagicMock(return_value=iter([]))

        tts_module.speak("")  # should not raise


# --- run_server (smoke test) ---

class TestRunServer:

    def test_run_server_writes_pid_and_binds_socket(self, tts_module, tmp_path):
        """run_server should create PID file, bind socket, and start accepting."""
        pid_path = tmp_path / "tts.pid"
        socket_path = tmp_path / "tts.sock"

        # Mock socket so we can control accept() and break the loop
        mock_server = MagicMock()
        mock_conn = MagicMock()
        # accept() returns a mock connection, then raise KeyboardInterrupt to exit
        mock_server.accept.side_effect = [
            (mock_conn, None),
            KeyboardInterrupt,
        ]
        # mock_conn context manager: `with conn:` should work
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        # recv returns b"" on first call to break inner loop
        mock_conn.recv.return_value = b""

        import os as _os
        with patch.object(tts_module, "PID_FILE", str(pid_path)):
            with patch.object(tts_module, "SOCKET", str(socket_path)):
                with patch.object(tts_module.socket, "socket", return_value=mock_server):
                    with patch("os.getpid", return_value=42):
                        # run_server blocks on accept, but we mocked it to
                        # return once then raise KeyboardInterrupt
                        try:
                            tts_module.run_server()
                        except KeyboardInterrupt:
                            pass

                # Verify PID file was written
                assert pid_path.exists()
                assert pid_path.read_text() == "42"

                # Verify socket was bound and listening
                mock_server.bind.assert_called_once_with(str(socket_path))
                mock_server.listen.assert_called_once_with(4)
