#!/usr/bin/env python3
"""Grok Build Stop hook: speak the final assistant message via Kokoro.

Reads the Stop event JSON from stdin. On a genuine end_turn with text,
and when /tmp/opencode-voice-enabled exists, cleans markdown and pipes
the last 800 characters to speak.sh asynchronously.

Never blocks the stop (always exits 0; no decision JSON on stdout).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Allow `from clean_for_speech import ...` when installed next to this file.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from clean_for_speech import clean_for_speech  # noqa: E402

VOICE_FLAG = "/tmp/opencode-voice-enabled"
SPEAK_SH = os.environ.get(
    "OPENCODE_VOICE_SPEAK",
    str(Path.home() / ".local/share/opencode-voice/speak.sh"),
)
MAX_CHARS = 800


def should_speak(payload: dict) -> str | None:
    """Return cleaned text to speak, or None to skip."""
    if payload.get("reason") != "end_turn":
        return None

    text = payload.get("lastAssistantMessage")
    if not isinstance(text, str) or not text.strip():
        return None

    if not os.path.exists(VOICE_FLAG):
        return None

    cleaned = clean_for_speech(text)
    if not cleaned:
        return None

    if len(cleaned) > MAX_CHARS:
        cleaned = cleaned[-MAX_CHARS:]

    return cleaned


def enqueue_speech(text: str, speak_sh: str = SPEAK_SH) -> None:
    """Fire-and-forget: send text to speak.sh without waiting for TTS."""
    proc = subprocess.Popen(
        [speak_sh],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    assert proc.stdin is not None
    try:
        proc.stdin.write(text.encode("utf-8"))
    except BrokenPipeError:
        pass
    finally:
        try:
            proc.stdin.close()
        except BrokenPipeError:
            pass


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return 0

    if not isinstance(payload, dict):
        return 0

    text = should_speak(payload)
    if text is None:
        return 0

    try:
        if not os.path.isfile(SPEAK_SH) or not os.access(SPEAK_SH, os.X_OK):
            return 0
        enqueue_speech(text)
    except OSError:
        pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
