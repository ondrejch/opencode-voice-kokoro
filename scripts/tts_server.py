#!/usr/bin/env python3
"""
Persistent Kokoro TTS daemon.

Keeps the Kokoro model loaded and listens on a Unix socket for
text-to-speech requests.  This avoids the Python/PyTorch startup
latency on every call, making TTS near-instantaneous.

Backend: set TTS_DEVICE to "cuda" or "cpu" (or env OPENCODE_TTS_DEVICE).

Usage:
    python tts_server.py

The server listens on /tmp/opencode-tts.sock.  Send text via socat:

    echo "Hello world" | socat - UNIX-CONNECT:/tmp/opencode-tts.sock
"""

import atexit
import os
import signal
import socket
import threading

import torch
import sounddevice as sd

from kokoro import KModel, KPipeline


SOCKET = "/tmp/opencode-tts.sock"
PID_FILE = "/tmp/opencode-tts.pid"
VOICE = "af_heart"
SPEED = 1.1

# TTS backend: "cuda" (GPU, default) or "cpu".
# Override without editing: export OPENCODE_TTS_DEVICE=cpu
TTS_DEVICE = os.environ.get("OPENCODE_TTS_DEVICE", "cuda").strip().lower()
if TTS_DEVICE not in ("cuda", "cpu"):
    raise SystemExit(
        f"Invalid TTS_DEVICE={TTS_DEVICE!r}; use 'cuda' or 'cpu'"
    )

stop_requested = threading.Event()

# Module-level defaults — overwritten when the server actually starts.
# Kept as None so speak() can be imported and tested without a GPU.
model = None
pipeline = None
voice = None


def cleanup():
    """Clean up socket and PID file, but only if they belong to this process.

    The PID file guards against atexit running in a different process
    (e.g. a test harness) and deleting the real server's socket.
    """
    try:
        with open(PID_FILE, encoding="utf-8") as f:
            owner_pid = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        # No PID file — nothing to clean up.
        return

    if owner_pid != os.getpid():
        # This PID file belongs to another process (e.g. the real
        # server while we're a test).  Don't touch its socket.
        return

    try:
        os.unlink(SOCKET)
    except FileNotFoundError:
        pass

    try:
        os.unlink(PID_FILE)
    except FileNotFoundError:
        pass


def request_stop(*_):
    stop_requested.set()
    try:
        sd.stop()
    except Exception:
        pass


def speak(text: str):
    stop_requested.clear()

    for _, phonemes, _ in pipeline(text, VOICE, SPEED):
        if stop_requested.is_set():
            break

        ref_s = voice[len(phonemes) - 1]

        with torch.inference_mode():
            audio = model(
                phonemes,
                ref_s,
                SPEED,
            )

        samples = audio.cpu().numpy()

        sd.play(samples, 24000)
        sd.wait()

        if stop_requested.is_set():
            break


def run_server():
    """Load the model, register signals, and start the accept loop.

    This is only called when the script is run directly
    (`python tts_server.py`).  Importing the module does not
    start the server — the functions and constants remain
    available for testing.
    """
    global model, pipeline, voice

    print(f"Loading Kokoro on {TTS_DEVICE}...")

    model = KModel().to(TTS_DEVICE).eval()

    pipeline = KPipeline(
        lang_code="a",
        model=False,
    )

    voice = pipeline.load_voice(VOICE)

    print(f"Kokoro ready ({TTS_DEVICE}).")

    signal.signal(signal.SIGUSR1, request_stop)
    atexit.register(cleanup)

    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))

    server = socket.socket(
        socket.AF_UNIX,
        socket.SOCK_STREAM,
    )

    try:
        os.unlink(SOCKET)
    except FileNotFoundError:
        pass

    server.bind(SOCKET)
    server.listen(4)

    print(f"Listening on {SOCKET}")

    while True:
        conn, _ = server.accept()

        with conn:
            chunks = []

            while True:
                data = conn.recv(65536)

                if not data:
                    break

                chunks.append(data)

            text = b"".join(chunks).decode().strip()

            if text:
                speak(text)


if __name__ == "__main__":
    run_server()
