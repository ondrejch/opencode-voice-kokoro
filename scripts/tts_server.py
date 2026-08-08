#!/usr/bin/env python3
"""
Persistent Kokoro TTS daemon.

Keeps the Kokoro model loaded on CUDA and listens on a Unix socket
for text-to-speech requests.  This avoids the Python/PyTorch startup
latency on every call, making TTS near-instantaneous.

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
stop_requested = threading.Event()
playback_stream = None

# Module-level defaults — overwritten when the server actually starts.
# Kept as None so speak() can be imported and tested without a GPU.
model = None
pipeline = None
voice = None


def cleanup():
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

    if playback_stream is not None:
        try:
            playback_stream.stop()
            playback_stream.abort()
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

        global playback_stream
        playback_stream = sd.play(samples, 24000)
        playback_stream.wait()

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

    print("Loading Kokoro on CUDA...")

    model = KModel().to("cuda").eval()

    pipeline = KPipeline(
        lang_code="a",
        model=False,
    )

    voice = pipeline.load_voice(VOICE)

    print("Kokoro ready.")

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
