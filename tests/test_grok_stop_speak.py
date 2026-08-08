"""Tests for scripts/grok_stop_speak.py Stop-hook logic."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "grok_stop_speak.py"


def _load_module():
    # Ensure clean_for_speech is importable from scripts/
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)

    spec = importlib.util.spec_from_file_location("grok_stop_speak", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["grok_stop_speak"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()


class TestShouldSpeak:
    def test_end_turn_with_text_and_flag(self, tmp_path, monkeypatch):
        flag = tmp_path / "voice-enabled"
        flag.write_text("")
        monkeypatch.setattr(mod, "VOICE_FLAG", str(flag))
        out = mod.should_speak(
            {"reason": "end_turn", "lastAssistantMessage": "Hello **world**"}
        )
        assert out == "Hello world"

    def test_skips_non_end_turn(self, tmp_path, monkeypatch):
        flag = tmp_path / "voice-enabled"
        flag.write_text("")
        monkeypatch.setattr(mod, "VOICE_FLAG", str(flag))
        assert (
            mod.should_speak(
                {"reason": "channel_closed", "lastAssistantMessage": "Bye"}
            )
            is None
        )
        assert (
            mod.should_speak({"reason": "shutdown", "lastAssistantMessage": "Bye"})
            is None
        )

    def test_skips_when_flag_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "VOICE_FLAG", str(tmp_path / "missing"))
        assert (
            mod.should_speak(
                {"reason": "end_turn", "lastAssistantMessage": "Hello"}
            )
            is None
        )

    def test_skips_empty_message(self, tmp_path, monkeypatch):
        flag = tmp_path / "voice-enabled"
        flag.write_text("")
        monkeypatch.setattr(mod, "VOICE_FLAG", str(flag))
        assert mod.should_speak({"reason": "end_turn", "lastAssistantMessage": ""}) is None
        assert (
            mod.should_speak({"reason": "end_turn", "lastAssistantMessage": "   "})
            is None
        )
        assert mod.should_speak({"reason": "end_turn"}) is None

    def test_truncates_to_last_800(self, tmp_path, monkeypatch):
        flag = tmp_path / "voice-enabled"
        flag.write_text("")
        monkeypatch.setattr(mod, "VOICE_FLAG", str(flag))
        long = "a" * 1000
        out = mod.should_speak(
            {"reason": "end_turn", "lastAssistantMessage": long}
        )
        assert out is not None
        assert len(out) == 800
        assert out == "a" * 800

    def test_skips_when_clean_is_empty(self, tmp_path, monkeypatch):
        flag = tmp_path / "voice-enabled"
        flag.write_text("")
        monkeypatch.setattr(mod, "VOICE_FLAG", str(flag))
        # Only a code block → cleaned empty
        assert (
            mod.should_speak(
                {
                    "reason": "end_turn",
                    "lastAssistantMessage": "```\ncode only\n```",
                }
            )
            is None
        )


class TestMain:
    def test_main_end_turn_enqueues(self, tmp_path, monkeypatch):
        flag = tmp_path / "voice-enabled"
        flag.write_text("")
        speak = tmp_path / "speak.sh"
        speak.write_text("#!/bin/sh\ncat >/dev/null\n")
        speak.chmod(0o755)

        monkeypatch.setattr(mod, "VOICE_FLAG", str(flag))
        monkeypatch.setattr(mod, "SPEAK_SH", str(speak))

        payload = {
            "reason": "end_turn",
            "lastAssistantMessage": "All tests passed.",
        }
        monkeypatch.setattr(
            sys, "stdin", type("S", (), {"read": lambda self: json.dumps(payload)})()
        )

        with patch.object(mod, "enqueue_speech") as mock_enq:
            assert mod.main() == 0
            mock_enq.assert_called_once_with("All tests passed.")

    def test_main_invalid_json_exits_zero(self, monkeypatch):
        monkeypatch.setattr(
            sys, "stdin", type("S", (), {"read": lambda self: "not-json{"})()
        )
        assert mod.main() == 0

    def test_main_empty_stdin(self, monkeypatch):
        monkeypatch.setattr(sys, "stdin", type("S", (), {"read": lambda self: ""})())
        assert mod.main() == 0

    def test_main_missing_speak_sh_skips(self, tmp_path, monkeypatch):
        flag = tmp_path / "voice-enabled"
        flag.write_text("")
        monkeypatch.setattr(mod, "VOICE_FLAG", str(flag))
        monkeypatch.setattr(mod, "SPEAK_SH", str(tmp_path / "nope.sh"))
        payload = {"reason": "end_turn", "lastAssistantMessage": "Hi"}
        monkeypatch.setattr(
            sys, "stdin", type("S", (), {"read": lambda self: json.dumps(payload)})()
        )
        with patch.object(mod, "enqueue_speech") as mock_enq:
            assert mod.main() == 0
            mock_enq.assert_not_called()
