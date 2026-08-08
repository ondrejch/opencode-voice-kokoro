#!/usr/bin/env python3
"""
Push-to-talk speech-to-text daemon for OpenCode.

Holds a configurable key to record microphone, releases to transcribe
with faster-whisper (large-v3 on CUDA), then injects the text into
the focused terminal via wtype (Wayland) or xdotool (X11).

Also kills any running Kokoro TTS process on key-press so you can
barge-in and interrupt OpenCode's speech.
"""

import subprocess
import tempfile
import threading
import os
import signal

import numpy as np
import sounddevice as sd
from evdev import InputDevice, ecodes
from faster_whisper import WhisperModel


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

SAMPLE_RATE = 16000

# --- PTT (Push-To-Talk) key ---
#
# These are hardcoded for the author's keyboard:
#   Microsoft 2.4GHz Transceiver v7.0
#
# The Home button (KEY_HOMEPAGE) lives on the Consumer Control
# interface, not the main keyboard interface.  Your keyboard will
# almost certainly have a different event path and possibly a
# different key code.
#
# To find yours:
#
#   1. Run `sudo evtest` and select each /dev/input/event* device.
#      Press the key you want to use for push-to-talk.  The output
#      will show something like:
#
#        Event: type 1 (EV_KEY), code 102 (KEY_RIGHTCTRL), value 1
#
#      The device path (e.g. /dev/input/event3) goes in PTT_PATH.
#      The code name (e.g. KEY_RIGHTCTRL) maps to ecodes.KEY_RIGHTCTRL.
#
#   2. If evtest does not show a symbolic name, use the numeric code
#      directly:  PTT_KEY = 180
#
#   3. Your user must be in the `input` group to read
#      /dev/input/event*:
#
#        sudo usermod -aG input "$USER"
#        (then log out and back in)
#
# -----------------

# The two PTT_PATH/PTT_KEY pairs below are examples from the author's
# keyboard.  They are the same physical keyboard exposed through two
# different USB interfaces.  In Python, only the last pair is active,
# so replace both examples with your own values or keep the pair you
# want active at the bottom.

# Right Ctrl on the main keyboard interface.
PTT_PATH = "/dev/input/event3"
PTT_KEY = ecodes.KEY_RIGHTCTRL

# Home button on the Consumer Control interface.  Shadows the above.
PTT_PATH = "/dev/input/event6"
PTT_KEY = ecodes.KEY_HOMEPAGE

MODEL_NAME = "large-v3"
TTS_PID_FILE = "/tmp/opencode-tts.pid"

model = WhisperModel(
    MODEL_NAME,
    device="cuda",
    compute_type="float16",
)


# ------------------------------------------------------------
# Audio recording
# ------------------------------------------------------------

recording = False
frames = []
stream = None


def stop_tts():
    try:
        with open(TTS_PID_FILE, encoding="utf-8") as f:
            pid = int(f.read().strip())

        # tts_server.py listens for SIGUSR1 and stops current playback.
        os.kill(pid, signal.SIGUSR1)
    except (FileNotFoundError, ProcessLookupError, ValueError):
        pass


def audio_callback(indata, frames_count, time_info, status):
    if status:
        print(status)

    if recording:
        frames.append(indata.copy())


def start_recording():
    global recording, frames, stream

    if recording:
        return

    # Barge-in: stop current TTS playback before opening the mic.
    stop_tts()

    frames = []
    recording = True

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=audio_callback,
    )

    stream.start()

    print("Listening...")


def stop_recording():
    global recording, stream

    if not recording:
        return

    recording = False

    stream.stop()
    stream.close()
    stream = None

    print("Transcribing...")

    if not frames:
        return

    audio = np.concatenate(frames, axis=0).flatten()

    duration = len(audio) / SAMPLE_RATE

    # Ignore accidental taps.
    if duration < 0.2:
        return

    transcribe(audio)


# ------------------------------------------------------------
# Whisper
# ------------------------------------------------------------

def transcribe(audio):
    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False,
    ) as tmp:
        wav_path = tmp.name

    try:
        import wave

        pcm = np.clip(audio, -1.0, 1.0)
        pcm = (pcm * 32767).astype(np.int16)

        with wave.open(wav_path, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(pcm.tobytes())

        segments, info = model.transcribe(
            wav_path,
            language="en",
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False,
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        if not text:
            print("Nothing recognized.")
            return

        print(f"You: {text}")

        type_into_opencode(text)

    finally:
        try:
            os.unlink(wav_path)
        except FileNotFoundError:
            pass


# ------------------------------------------------------------
# Inject transcription into terminal
# ------------------------------------------------------------

def type_into_opencode(text):
    """Type text into the focused terminal.  Wayland (wtype) first,
    X11 (xdotool) as fallback."""

    session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    wayland_display = os.environ.get("WAYLAND_DISPLAY")

    if session == "wayland" and wayland_display:
        result = subprocess.run(
            ["wtype", "--", text],
            check=False,
        )

        if result.returncode == 0:
            return

    # X11 fallback
    subprocess.run(
        [
            "xdotool",
            "type",
            "--clearmodifiers",
            "--delay",
            "1",
            text,
        ],
        check=False,
    )


# ------------------------------------------------------------
# Keyboard
# ------------------------------------------------------------

def find_keyboard():
    dev = InputDevice(PTT_PATH)

    print(f"Keyboard: {dev.path}  {dev.name}")
    return dev


def keyboard_loop():
    dev = find_keyboard()

    print()
    print("READY")
    print(f"Hold keycode {PTT_KEY} to talk.")
    print(f"Release keycode {PTT_KEY} to transcribe.")
    print()

    for event in dev.read_loop():

        if event.type != ecodes.EV_KEY:
            continue

        if event.code != PTT_KEY:
            continue

        # key press
        if event.value == 1:
            start_recording()

        # key release
        elif event.value == 0:
            threading.Thread(
                target=stop_recording,
                daemon=True,
            ).start()


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":
    print("Loading Whisper large-v3 on CUDA...")
    print("Model loaded.")

    keyboard_loop()
