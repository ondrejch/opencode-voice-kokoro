# Control OpenCode via Voice

**User:** Anonymous  
**Created:** 8/7/2026 10:03:40  
**Updated:** 8/8/2026 0:20:35  
**Exported:** 8/8/2026 0:21:57  
**Link:** [https://chatgpt.com/g/g-p-6a6d2729d2e481919e8f707a874f5989/c/6a75e5a6-c720-83ea-8cc6-f8a87acef397](https://chatgpt.com/g/g-p-6a6d2729d2e481919e8f707a874f5989/c/6a75e5a6-c720-83ea-8cc6-f8a87acef397)  

## Prompt:
8/7/2026, 10:03:39 AM

control opencode from voice on linux

## Response:
8/7/2026, 10:03:40 AM

> **Searching OpenCode CLI Linux voice control speech to text terminal 2026**
>
> [Intro | AI coding agent built for the terminal](https://opencode.ai/docs)
> [GitHub - opencode-ai/opencode: A powerful AI coding agent. Built for the terminal. · GitHub](https://github.com/opencode-ai/opencode)
> [CLI | OpenCode](https://dev.opencode.ai/docs/cli/)
> [OpenCode | Documentation](https://opencode-ai.com/en/docs.html)
> [CLI | opencode](https://thdxr.dev.opencode.ai/docs/cli/)
> [CLI Command Reference - AI 编程助手实战指南](https://opencode.runman.ai/en/appendix/cli.html)
> [文档 - OpenCode 中文文档](https://opencodeai.cn/docs.html)
> [Install OpenCode on Linux | Snap Store](https://snapcraft.io/opencode)
> [Remote-OpenCode v1.4.0 - Voice Mode Updated!](https://www.reddit.com/r/opencodeCLI/comments/1rpxzum/remoteopencode_v140_voice_mode_updated/)
> [YazSes: An Offline, Privacy-First, Cross-Platform Hold-to-Talk Voice-Dictation System](https://arxiv.org/abs/2607.28878)
>
> **Searched 10 websites**
>
> 
>
> Worked for 4s

Yes. On Linux, the cleanest setup is usually **push-to-talk speech-to-text that injects text into the focused terminal**, rather than trying to make OpenCode itself handle audio. OpenCode’s terminal UI already accepts normal prompt text, so this works without modifying OpenCode. ([OpenCode](https://opencode.ai/docs?utm_source=chatgpt.com))

For your local-LLM setup, I’d consider three approaches:

- **Best general solution: YazSes** - local/offline push-to-talk dictation built specifically for Linux/macOS/Windows. It uses `faster-whisper`, injects transcription into the focused application, and can also map spoken phrases to commands. That means you could hold a key, say “inspect the current implementation and fix the failing tests,” release, and have it appear directly in the OpenCode prompt. The recently published implementation is CPU-capable and privacy-oriented. ([arXiv](https://arxiv.org/abs/2607.28878?utm_source=chatgpt.com))
- **OpenCode-specific voice plugin** - there are community OpenCode voice-input implementations/plugins, including push-to-talk approaches intended to feed transcription straight into OpenCode. They’re potentially more integrated but less standardized than generic Linux dictation. ([Reddit](https://www.reddit.com/r/opencodeCLI/comments/1ucyid6/is_there_a_way_to_use_voice_dictation_in_opencode/?utm_source=chatgpt.com))
- **Remote voice control** - if the point is to walk around and control the workstation from your phone, projects such as Remote-OpenCode accept voice messages, transcribe them, and forward the resulting prompt to the local OpenCode process. ([Reddit](https://www.reddit.com/r/opencodeCLI/comments/1rpxzum/remoteopencode_v140_voice_mode_updated/?utm_source=chatgpt.com))

For **desktop use**, I would build it like this:

```text
microphone
   ↓
push-to-talk hotkey
   ↓
faster-whisper / whisper.cpp
   ↓
transcribed text
   ↓
focused terminal / OpenCode prompt
   ↓
Enter
```

You can make this considerably nicer than ordinary dictation by reserving a few voice commands, for example:

```text
"send"          → Enter
"cancel"        → Ctrl+C / Escape
"new session"   → OpenCode new-session command
"undo that"     → inject an appropriate OpenCode instruction
"clear prompt"  → Ctrl+U
```

For coding prompts, I would **not automatically send when you stop speaking**. Have speech populate the OpenCode input field, inspect/edit it for a second if necessary, then say a command such as “send” or hit Enter. Whisper occasionally mangles identifiers, paths, flags, and model names, and an accidental agentic instruction can have much larger consequences than a typo in ordinary dictation.

Given your existing local GPU setup, another attractive configuration is:

```text
OpenCode → Qwen3.6-27B on your RTX 6000 Pro
voice STT → faster-whisper small/medium or whisper.cpp
```

Keep STT on CPU if you don't want it competing with the LLM for VRAM; the recently published YazSes measurements show `faster-whisper` can operate faster than realtime on commodity CPU hardware. ([arXiv](https://arxiv.org/abs/2607.28878?utm_source=chatgpt.com))

If you want, I can give you a **concrete Ubuntu 24.04 setup with a global push-to-talk key (e.g. Right Ctrl), local Whisper, and automatic text injection into the OpenCode terminal**.

---

**Sources:**

- [Intro | AI coding agent built for the terminal](https://opencode.ai/docs?utm_source=chatgpt.com)
- [YazSes: An Offline, Privacy-First, Cross-Platform Hold-to-Talk Voice-Dictation System](https://arxiv.org/abs/2607.28878?utm_source=chatgpt.com)
- [Is there a way to use voice dictation in OpenCode instead of typing prompts?](https://www.reddit.com/r/opencodeCLI/comments/1ucyid6/is_there_a_way_to_use_voice_dictation_in_opencode/?utm_source=chatgpt.com)

## Prompt:
8/7/2026, 10:04:59 AM

I have plenty spare VRAM

## Response:
8/7/2026, 10:05:00 AM

> **Searching faster-whisper CUDA Linux installation GPU VRAM CTranslate2 official documentation**
>
> [GitHub - abotsis/whisper.cpp: Port of OpenAI's Whisper model in C/C++ · GitHub](https://github.com/abotsis/whisper.cpp)
> [faster-whisper2 · PyPI](https://pypi.org/project/faster-whisper2/)
> [[UPDATE]  Vocalinux v0.6.0-beta: 10x faster installs, universal GPU support, and a complete overhaul since v0.2.0-alpha](https://www.reddit.com/r/linux/comments/1r2kqvp/update_vocalinux_v060beta_10x_faster_installs/)
> [CUDA Tutorial -- Cryptanalysis of Classical Ciphers Using Modern GPUs and CUDA](https://arxiv.org/abs/2103.13937)
>
> **Searched 4 websites**
>
> 
>
> Worked for 4s

Then I’d use the GPU for speech recognition too. With an RTX 6000-class card and spare VRAM, **`faster-whisper` + CUDA** is the obvious choice: it uses CTranslate2, supports GPU inference, and its documented GPU setup targets CUDA 12.x. ([GitHub](https://github.com/SYSTRAN/faster-whisper/blob/master/README.md?plain=1&utm_source=chatgpt.com))

For voice-driving OpenCode, I’d use a larger Whisper model than I would on CPU:

```text
microphone
  ↓
push-to-talk
  ↓
faster-whisper large-v3 / distil-large-v3 on CUDA
  ↓
text injection into terminal
  ↓
OpenCode
```

`large-v3` is attractive here because coding dictation is unusually unforgiving: filenames, flags, package names, numbers, and punctuation matter. If latency becomes noticeable, switch to `distil-large-v3`; for short push-to-talk prompts, either should be very responsive on your GPU.

A typical initialization is:

```python
from faster_whisper import WhisperModel

model = WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16",
)
```

I would use **FP16 rather than an aggressively quantized STT model** since you aren't VRAM-constrained. The additional memory saved by INT8 buys you little here, while transcription accuracy matters more.

There’s also a useful architectural detail with your setup: your Qwen model and Whisper can coexist on the same GPU. Whisper's workload is bursty-it runs only for a fraction of a second after you finish speaking-so it usually won't meaningfully interfere with OpenCode generation, assuming you really have VRAM headroom.

For the interface, I'd make it:

```text
hold Right Alt
    ↓
record

release Right Alt
    ↓
GPU transcription
    ↓
paste into OpenCode

Right Alt + Enter
    ↓
transcribe + submit
```

That gives you **two modes**: release-to-dictate lets you inspect questionable identifiers before sending; the second shortcut is convenient when you're confident and want essentially conversational control.

On Wayland, text injection is commonly handled with `wtype`; on X11, `xdotool` works well. A recent Linux dictation implementation specifically uses `wtype` for Wayland and `evdev` for global hotkeys while running `faster-whisper` as the ASR backend. ([Reddit](https://www.reddit.com/r/linux/comments/1s6xs0g/i_ported_my_local_voice_dictation_tool_to_linux/?utm_source=chatgpt.com))

Given the hardware you described previously, I'd actually skip existing voice-control frameworks and make this as a **small ~100-line Python daemon**. It can have OpenCode-specific spoken commands like:

```text
"send it"           → Enter
"cancel"            → Esc
"interrupt"         → Ctrl+C
"clear"             → Ctrl+U
"new line"          → Shift+Enter
"slash models"      → /models
"undo last sentence"→ edit transcription buffer
```

That would be more reliable than trying to teach a generic desktop dictation app about OpenCode.

If you want, I can give you the complete **Ubuntu 24.04 + NVIDIA + faster-whisper + Wayland/X11 push-to-talk script**, including the systemd user service and hotkey handling.

---

**Sources:**

- [faster-whisper/README.md at master · SYSTRAN/faster-whisper · GitHub](https://github.com/SYSTRAN/faster-whisper/blob/master/README.md?plain=1&utm_source=chatgpt.com)
- [I ported my local voice dictation tool to Linux — Wayland-native, faster-whisper, AppImage available](https://www.reddit.com/r/linux/comments/1s6xs0g/i_ported_my_local_voice_dictation_tool_to_linux/?utm_source=chatgpt.com)

## Prompt:
8/7/2026, 10:05:34 AM

I also want to to talk back if possible

## Response:
8/7/2026, 10:05:35 AM

> **Searching Linux local TTS realtime GPU Piper XTTS Kokoro 2026 OpenCode voice assistant**
>
> [@semirhuduti/opencode-tts-voice - npm](https://www.npmjs.com/package/%40semirhuduti/opencode-tts-voice)
> [Self-Hosted TTS Comparison: Bark, XTTS, Kokoro, Piper GIGAGPU](https://gigagpu.com/self-hosted-tts-comparison/)
> [interrupt — OpenCode Plugin by Aito's Intelligence](https://interrupt.camaramagic.com/)
> [Intro | AI coding agent built for the terminal](https://opencode.ai/en/docs)
> [I created a Text-to-speach plugin for opencode](https://www.reddit.com/r/opencode/comments/1szep3t/i_created_a_texttospeach_plugin_for_opencode/)
> [opencode-voice | renjfk / renos.tk revival](https://renjfk.com/artifacts/opencode-voice)
> [GitHub - anomalyco/opencode: The open source coding agent. · GitHub](https://github.com/anomalyco/opencode)
> [Getting Started | renjfk/opencode-voice | DeepWiki](https://deepwiki.com/renjfk/opencode-voice/1.1-getting-started)
> [JSPM – @renjfk/opencode-voice@0.5.0](https://jspm-packages.deno.dev/package/%40renjfk/opencode-voice%400.5.0)
> [Plugins | OpenCode](https://opencode.ubitools.com/plugins/)
> [XTTS: a Massively Multilingual Zero-Shot Text-to-Speech Model](https://arxiv.org/abs/2406.04904)
>
> **Searched 11 websites**
>
> 
>
> Worked for 4s

Yes. In fact, for OpenCode there are now **integrated voice plugins that do both STT and TTS**, so I would use one of those rather than glue together generic desktop dictation and a separate speech daemon.

The most relevant option is **`opencode-voice`**. It provides speech-to-text and text-to-speech directly inside the OpenCode TUI, using `whisper.cpp` for input and Piper for local synthesis, with an optional OpenAI-compatible LLM normalization layer for technical terms and identifiers. ([renjfk / renos.tk revival](https://renjfk.com/artifacts/opencode-voice?utm_source=chatgpt.com))

For your hardware, though, I’d probably improve the TTS side beyond Piper. Piper is extremely fast but fairly utilitarian. With spare GPU memory, **Kokoro** is a good quality/latency sweet spot, and there is already an OpenCode TTS plugin using Kokoro entirely locally. ([Reddit](https://www.reddit.com/r/opencode/comments/1szep3t/i_created_a_texttospeach_plugin_for_opencode/?utm_source=chatgpt.com))

So my preferred architecture would be roughly:

```text
                    ┌─ faster-whisper / Whisper GPU
microphone ────────►│
                    ▼
                OpenCode
                    │
                    │ response text
                    ▼
               Kokoro TTS
                    │
                    ▼
             speakers/headphones
```

The really useful feature is **barge-in/interruption**. You don't want to wait for a 45-second explanation to finish speaking before correcting the agent. There is an OpenCode interruption plugin specifically designed for this: you speak while TTS is playing, it stops the current speech and injects the correction into OpenCode. ([Reddit](https://www.reddit.com/r/opencode/comments/1u1z2gi/i_built_a_walkietalkie_plugin_for_opencode_ptt_to/?utm_source=chatgpt.com))

That gives you interaction much closer to:

> **You:** Refactor the server startup so it uses the new vLLM endpoint.  
> **OpenCode:** I've found three places where the endpoint is-  
> **You:** No, leave the fallback endpoint unchanged.  
> **OpenCode:** Understood. I'll only modify the primary endpoint...

rather than conventional push-to-talk transcription.

### What I'd build on your machine

Given your spare RTX VRAM, I'd favor:

```text
STT:
faster-whisper large-v3
CUDA FP16

LLM:
your existing Qwen3.6-27B server

TTS:
Kokoro
GPU

Control:
push-to-talk key
+
barge-in detection
```

I would **not have OpenCode literally read its entire terminal output**. Coding agents produce lots of things that are terrible spoken aloud:

```text
diffs
paths
stack traces
JSON
tool calls
compiler output
long code blocks
```

Instead, have a tiny TTS filter speak only natural-language agent messages and suppress code/tool output. For example:

```text
OpenCode output

"Changed 3 files."
              ───────────► speak

```diff
- foo()
+ bar()
```
              ───────────► don't speak

"Tests now pass. There is one remaining warning."
              ───────────► speak
```

Even better, tell the model through your system prompt:

```text
When voice mode is active, end substantial turns with a short
spoken-status sentence suitable for TTS.

Do not include paths, code, hashes, or commands in that sentence
unless necessary.
```

Then the screen can contain the full technical response while TTS only says something like:

> “The change is complete and all tests pass. I found one unrelated warning that I left unchanged.”

That's much more usable.

There is also an existing package called `@semirhuduti/opencode-tts-voice` with controls specifically for things like speaking responses, speaking subagent responses, idle announcements, speech chunk sizes, and pauses. ([npm](https://www.npmjs.com/package/%40semirhuduti/opencode-tts-voice?utm_source=chatgpt.com))

So I'd rank the approaches:

1. **Best experience:** faster-whisper + Kokoro + OpenCode plugin + barge-in.
2. **Least setup:** `opencode-voice` with Whisper + Piper.
3. **Interesting ready-made conversational approach:** `speech-opencode` + `opencode-interrupt-plugin`, which already implements TTS, Whisper input, and voice interruption. ([Interrupt](https://interrupt.camaramagic.com/?utm_source=chatgpt.com))

With your GPU, **#1 is the setup I'd pursue**. The important part isn't actually the speech quality; it's getting **streaming TTS + immediate interruption + intelligent suppression of code/tool output** right. That turns OpenCode into something you can genuinely converse with while it works, rather than merely a terminal with dictation.

---

**Sources:**

- [opencode-voice | renjfk / renos.tk revival](https://renjfk.com/artifacts/opencode-voice?utm_source=chatgpt.com)
- [I created a Text-to-speach plugin for opencode](https://www.reddit.com/r/opencode/comments/1szep3t/i_created_a_texttospeach_plugin_for_opencode/?utm_source=chatgpt.com)
- [@semirhuduti/opencode-tts-voice - npm](https://www.npmjs.com/package/%40semirhuduti/opencode-tts-voice?utm_source=chatgpt.com)
- [interrupt — OpenCode Plugin by Aito's Intelligence](https://interrupt.camaramagic.com/?utm_source=chatgpt.com)

## Prompt:
8/7/2026, 10:07:56 AM

show how to implement it

## Response:
8/7/2026, 10:07:57 AM

I’d implement this as two small local services plus one OpenCode plugin: **GPU STT for push-to-talk**, **GPU TTS for replies**, and the plugin as the glue. That keeps OpenCode itself simple and makes interruption/barge-in manageable.

> **Searching OpenCode plugin API docs events assistant message hooks TTS 2026**
>
> [OpenCode Plugins: Extend with TypeScript & Hooks - OpenCode Docs](https://open-code.ai/en/docs/plugins)
> [GitHub - SYSTRAN/faster-whisper: Faster Whisper transcription with ...](https://github.com/SYSTRAN/faster-whisper)
> [Plugins - OpenCode](https://opencode.ai/v2/docs/build/plugins)
> [faster-whisper · PyPI](https://pypi.org/project/faster-whisper/)
> [Running TTS Locally — How We Ditched OpenAI's Voice API for a GPU Rig](https://thinksmart.life/research/posts/local-tts-kokoro-gpu-rig/)
> [OpenCode Plugin Development: Custom Tools & Event Hooks Guide - Lushbinary](https://lushbinary.com/blog/opencode-plugin-development-custom-tools-hooks-guide/)
> [faster-whisper CUDA Setup: Local Whisper Transcription, VAD, and Batching](https://knightli.com/en/2026/05/01/faster-whisper-speech-to-text/)
> [Whisper-AuT: Domain-Adapted Audio Encoder for Efficient Audio-LLM Training](https://arxiv.org/abs/2604.10438)
>
> **Searched 8 websites**
>
> 
>
> **Searching the web**
>
> [Plugins | OpenCode](https://opencode.ai/docs/plugins/)
> [GitHub - SYSTRAN/faster-whisper: Faster Whisper transcription with CTranslate2 · GitHub](https://github.com/SYSTRAN/faster-whisper)
> [kokoro-tts · PyPI](https://pypi.org/project/kokoro-tts/)
>
> **Searched 3 websites**
>
> 
>
> Worked for 10s

Given your setup, I’d start with a **minimal robust version** rather than full duplex immediately:

1. Hold a key → record microphone.
2. Release → `faster-whisper large-v3` on CUDA.
3. Inject transcription into OpenCode’s prompt.
4. When OpenCode finishes a turn, speak a cleaned summary using Kokoro.
5. Any new push-to-talk press immediately kills TTS, giving you practical barge-in.

OpenCode supports global local plugins under `~/.config/opencode/plugins/`, exposes message/session events, and specifically has TUI hooks such as `tui.prompt.append`. ([OpenCode](https://opencode.ai/docs/plugins/)) Faster-whisper officially supports `large-v3` with CUDA FP16. ([GitHub](https://github.com/SYSTRAN/faster-whisper))

## 1. Install the audio/STT dependencies

On Ubuntu:

```bash
sudo apt install ffmpeg pipewire-audio playerctl \
    libportaudio2 portaudio19-dev python3.12-venv

mkdir -p ~/.local/share/opencode-voice
cd ~/.local/share/opencode-voice

python3.12 -m venv .venv
source .venv/bin/activate

pip install faster-whisper sounddevice soundfile numpy
```

For your GPU, use:

```python
WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16",
)
```

That's exactly the supported faster-whisper GPU configuration. ([GitHub](https://github.com/SYSTRAN/faster-whisper))

I'd keep `beam_size=5` initially. Once everything works, benchmark `beam_size=1` against it; for short coding commands the latency reduction may be worth the tiny accuracy loss.

---

# 2. STT daemon

Create:

```bash
mkdir -p ~/.local/share/opencode-voice
nano ~/.local/share/opencode-voice/voice.py
```

Use this:

```python
#!/usr/bin/env python3

import os
import signal
import subprocess
import tempfile
import threading
import time

import numpy as np
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
CHANNELS = 1

MODEL = WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16",
)

recording = False
frames = []
stream = None

TTS_PID_FILE = "/tmp/opencode-tts.pid"

def stop_tts():
    try:
        with open(TTS_PID_FILE) as f:
            pid = int(f.read().strip())

        os.kill(pid, signal.SIGTERM)

    except (FileNotFoundError, ValueError, ProcessLookupError):
        pass

def callback(indata, frame_count, time_info, status):
    if status:
        print(status)

    if recording:
        frames.append(indata.copy())

def start_recording():
    global recording, frames, stream

    if recording:
        return

    # This is our "barge in":
    # speaking immediately stops OpenCode's current speech.
    stop_tts()

    frames = []
    recording = True

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        callback=callback,
    )

    stream.start()

    print("recording...")

def stop_recording():
    global recording, stream

    if not recording:
        return

    recording = False

    stream.stop()
    stream.close()
    stream = None

    if not frames:
        return

    audio = np.concatenate(frames, axis=0)

    # Ignore accidental extremely short presses.
    duration = len(audio) / SAMPLE_RATE

    if duration < 0.25:
        return

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as tmp:
        path = tmp.name

    sf.write(path, audio, SAMPLE_RATE)

    try:
        segments, info = MODEL.transcribe(
            path,
            language="en",
            beam_size=5,
            vad_filter=True,
            vad_parameters={
                "min_silence_duration_ms": 250,
            },
            condition_on_previous_text=False,
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        if text:
            print(">", text)
            inject_into_opencode(text)

    finally:
        os.unlink(path)

def inject_into_opencode(text):
    #
    # We will replace this next with OpenCode-native injection.
    # First version uses wtype on Wayland.
    #
    subprocess.run(
        ["wtype", "--", text],
        check=False,
    )

if __name__ == "__main__":
    print("Whisper loaded")
    print("Use SIGUSR1=start, SIGUSR2=stop")

    signal.signal(
        signal.SIGUSR1,
        lambda *_: start_recording()
    )

    signal.signal(
        signal.SIGUSR2,
        lambda *_: threading.Thread(
            target=stop_recording,
            daemon=True
        ).start()
    )

    while True:
        time.sleep(3600)
```

Install `wtype` if you're on Wayland:

```bash
sudo apt install wtype
```

Faster-whisper includes Silero VAD and exposes `vad_filter` plus configurable silence thresholds, so the filtering above isn't another dependency. ([GitHub](https://github.com/SYSTRAN/faster-whisper))

Test:

```bash
source ~/.local/share/opencode-voice/.venv/bin/activate
python ~/.local/share/opencode-voice/voice.py
```

From another terminal:

```bash
pgrep -f 'opencode-voice/voice.py'
```

Suppose PID is `12345`.

Start recording:

```bash
kill -USR1 12345
```

Speak.

Stop:

```bash
kill -USR2 12345
```

Your speech should appear in the currently focused terminal.

---

# 3. Bind it to a key

You have a few choices depending on desktop environment.

If you're using KDE, GNOME, Hyprland, etc., the easiest first version is **two shortcuts**:

```bash
pkill -USR1 -f 'opencode-voice/voice.py'
```

and:

```bash
pkill -USR2 -f 'opencode-voice/voice.py'
```

But what you really want is:

```text
key down   → SIGUSR1
key up     → SIGUSR2
```

For proper hold-to-talk, I'd use `evdev` so it works independently of Wayland's global hotkey restrictions.

Install:

```bash
source ~/.local/share/opencode-voice/.venv/bin/activate
pip install evdev
```

Create:

```bash
nano ~/.local/share/opencode-voice/ptt.py
```

Example using Right Ctrl:

```python
#!/usr/bin/env python3

import os
import signal
import subprocess
import time

from evdev import InputDevice, ecodes, list_devices

VOICE_PATTERN = "opencode-voice/voice.py"

def find_keyboard():
    for path in list_devices():
        dev = InputDevice(path)

        caps = dev.capabilities()

        if ecodes.EV_KEY not in caps:
            continue

        keys = caps[ecodes.EV_KEY]

        if ecodes.KEY_RIGHTCTRL in keys:
            print("Using:", dev.path, dev.name)
            return dev

    raise RuntimeError("No suitable keyboard found")

def get_voice_pid():
    result = subprocess.run(
        ["pgrep", "-f", VOICE_PATTERN],
        capture_output=True,
        text=True,
    )

    pids = [
        int(x)
        for x in result.stdout.split()
        if x.strip()
    ]

    if not pids:
        raise RuntimeError("voice.py isn't running")

    return pids[0]

dev = find_keyboard()

voice_pid = get_voice_pid()

for event in dev.read_loop():

    if event.type != ecodes.EV_KEY:
        continue

    if event.code != ecodes.KEY_RIGHTCTRL:
        continue

    # 1 = key down
    if event.value == 1:
        os.kill(voice_pid, signal.SIGUSR1)

    # 0 = key up
    elif event.value == 0:
        os.kill(voice_pid, signal.SIGUSR2)
```

You may need access to `/dev/input/event*`.

Typically:

```bash
sudo usermod -aG input "$USER"
```

then log out/in.

Now:

```text
hold Right Ctrl
    ↓
talk
    ↓
release
    ↓
Whisper large-v3
    ↓
text appears in OpenCode
```

---

# 4. Make OpenCode speak

Now the interesting half.

Install Kokoro:

```bash
source ~/.local/share/opencode-voice/.venv/bin/activate
pip install kokoro-tts
```

The current `kokoro-tts` package supports stdin, selectable voices, speed control, WAV output and streaming playback. ([PyPI](https://pypi.org/project/kokoro-tts/))

You can verify it independently:

```bash
echo 'The tests passed successfully.' |
    kokoro-tts - --stream \
    --voice af_heart \
    --speed 1.1
```

If you prefer a male voice:

```bash
echo 'The tests passed successfully.' |
    kokoro-tts - --stream \
    --voice am_michael \
    --speed 1.1
```

The package currently exposes numerous US/UK/etc. voices including `af_heart`, `af_sarah`, `am_michael`, `am_onyx`, and others. ([PyPI](https://pypi.org/project/kokoro-tts/))

---

# 5. A TTS wrapper with interruption

Create:

```bash
nano ~/.local/share/opencode-voice/speak.sh
```

```bash
#!/bin/bash

set -eu

PIDFILE=/tmp/opencode-tts.pid

cleanup() {
    rm -f "$PIDFILE"
}

trap cleanup EXIT INT TERM

echo $$ > "$PIDFILE"

exec ~/.local/share/opencode-voice/.venv/bin/kokoro-tts \
    - \
    --stream \
    --voice af_heart \
    --speed 1.08
```

Make executable:

```bash
chmod +x ~/.local/share/opencode-voice/speak.sh
```

Now:

```bash
echo 'Compilation succeeded with one warning.' |
    ~/.local/share/opencode-voice/speak.sh
```

The earlier Python code calls:

```python
stop_tts()
```

as soon as you press push-to-talk.

So:

```text
OpenCode speaking...
         ↓
you press Right Ctrl
         ↓
SIGTERM sent to Kokoro
         ↓
speech stops immediately
         ↓
microphone starts
```

That is your first version of **barge-in**.

---

# 6. OpenCode plugin

Now put the integration where it belongs:

```bash
mkdir -p ~/.config/opencode/plugins
nano ~/.config/opencode/plugins/voice.ts
```

OpenCode automatically loads `.js` or `.ts` files from `~/.config/opencode/plugins/` at startup. ([OpenCode](https://opencode.ai/docs/plugins/))

I'd start with:

```typescript
import type { Plugin } from "@opencode-ai/plugin"

const TTS =
  `${process.env.HOME}/.local/share/opencode-voice/speak.sh`

function cleanForSpeech(text: string): string {
  return text
    // fenced code
    .replace(/```[\s\S]*?```/g, " ")

    // inline code
    .replace(/`[^`]+`/g, " ")

    // markdown links
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")

    // crude paths
    .replace(/(?:\/[\w.\-]+){2,}/g, " ")

    // URLs
    .replace(/https?:\/\/\S+/g, " ")

    // whitespace
    .replace(/\s+/g, " ")

    .trim()
}

export const VoicePlugin: Plugin = async ({
  client,
  $
}) => {

  let accumulated = ""

  return {

    event: async ({ event }) => {

      /*
       * Accumulate assistant text.
       *
       * We'll inspect actual event payload once using logging,
       * because event schemas can change between OpenCode builds.
       */

      if (event.type === "message.part.updated") {

        const part = (event as any).properties?.part

        if (
          part?.type === "text" &&
          typeof part.text === "string"
        ) {
          accumulated = part.text
        }
      }

      if (event.type === "session.idle") {

        const text = cleanForSpeech(accumulated)

        accumulated = ""

        if (!text)
          return

        const spoken =
          text.length > 800
            ? text.slice(-800)
            : text

        await $`echo ${spoken} | ${TTS}`
      }
    },
  }
}
```

OpenCode exposes `message.part.updated`, `message.updated`, and `session.idle` events, so those are the right primitives for this integration. ([OpenCode](https://opencode.ai/docs/plugins/))

One caveat: OpenCode's public plugin page enumerates the events but doesn't document every current event payload in enough detail to justify hard-coding it blindly. I would therefore instrument it once.

Replace the handler temporarily with:

```typescript
event: async ({ event }) => {

  if (
    event.type === "message.part.updated" ||
    event.type === "message.updated"
  ) {
    await client.app.log({
      body: {
        service: "voice-debug",
        level: "info",
        message: JSON.stringify(event),
      },
    })
  }
}
```

OpenCode explicitly recommends `client.app.log()` for structured plugin logging. ([OpenCode](https://opencode.ai/docs/plugins/))

Run one normal interaction and inspect the OpenCode logs. Then match the exact `part` payload your current version emits.

---

# 7. Don't speak the whole answer

This matters a lot.

Suppose OpenCode emits:

```markdown
I changed the CUDA initialization.

```python
model = WhisperModel(...)
```

The tests now pass.

Files changed:
- src/asr.py
- src/config.py

The remaining warning is unrelated.
```

You don't want to hear all that.

I'd change your OpenCode global instruction to include something like:

```text
When voice interaction is enabled, finish each substantive
assistant turn with:

<voice>
one or two short natural-language sentences summarizing
the result or the next decision required from the user
</voice>

Do not include code, file paths, hashes, URLs, commands,
or stack traces inside <voice>.
```

Then make the plugin extract only:

```typescript
function extractVoice(text: string): string | null {

  const match = text.match(
    /<voice>([\s\S]*?)<\/voice>/i
  )

  if (!match)
    return null

  return match[1]
    .replace(/\s+/g, " ")
    .trim()
}
```

And:

```typescript
const spoken = extractVoice(accumulated)

if (!spoken)
    return

await $`echo ${spoken} | ${TTS}`
```

This is substantially better than regex-cleaning arbitrary agent output.

Your screen remains:

```text
full technical response
full diffs
compiler output
paths
commands
```

while you hear:

> “I updated the server configuration and the tests pass. There is one unrelated warning remaining.”

That's the interaction model I'd use.

---

# 8. OpenCode-native prompt injection

The `wtype` approach works, but it's slightly ugly because it depends on focus.

OpenCode has TUI events including:

```text
tui.prompt.append
tui.command.execute
tui.toast.show
```

([OpenCode](https://opencode.ai/docs/plugins/))

So the next improvement is to have your STT process communicate with an OpenCode plugin over a Unix socket:

```text
Whisper
   │
   │ Unix socket
   ▼
OpenCode voice plugin
   │
   ▼
tui.prompt.append
```

instead of:

```text
Whisper
   ↓
wtype
   ↓
Wayland
   ↓
terminal emulator
   ↓
OpenCode
```

That gets rid of focus problems entirely.

I would implement this after the basic voice loop works.

---

# 9. Suggested final architecture

Ultimately:

```text
                         RTX GPU
                ┌──────────────────────┐
                │                      │
microphone ────►│ faster-whisper      │
                │ large-v3 FP16        │
                │                      │
                └──────────┬───────────┘
                           │
                           │ text
                           ▼
                 ┌──────────────────┐
                 │ voice daemon     │
                 └────────┬─────────┘
                          │ Unix socket
                          ▼
                 ┌──────────────────┐
                 │ OpenCode plugin  │
                 │                  │
                 │ prompt append    │
                 │ message events   │
                 │ voice extraction │
                 └────────┬─────────┘
                          │
                          │ <voice>...
                          ▼
                ┌──────────────────────┐
                │ Kokoro GPU TTS       │
                └──────────┬───────────┘
                           │
                           ▼
                       speakers
```

And push-to-talk becomes the universal interrupt:

```text
                    OpenCode is speaking
                            │
                 press push-to-talk
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
         kill TTS                   start recording
                                           │
                                           ▼
                                      transcribe
                                           │
                                           ▼
                                   append to OpenCode
```

## One change to my earlier recommendation

I would **not start with continuous voice activity detection/barge-in** where the microphone constantly monitors you while TTS is playing. Your speakers can feed Kokoro's own voice back into Whisper and create an acoustic-echo problem.

Start with **push-to-talk barge-in**:

> press key → TTS instantly stops → mic opens.

That is deterministic and should feel excellent.

Once that's solid, you can add PipeWire echo cancellation and true hands-free interruption.

For your machine, I think this combination is the sweet spot:

```text
STT     faster-whisper large-v3 FP16
PTT     evdev
IPC     Unix domain socket
Agent   OpenCode
LLM     Qwen3.6-27B
TTS     Kokoro
Barge   PTT immediately SIGTERMs TTS
```

It remains entirely local, uses your spare GPU capacity, and doesn't require modifying OpenCode itself.

---

**Sources:**

- [Plugins | OpenCode](https://opencode.ai/docs/plugins/)
- [GitHub - SYSTRAN/faster-whisper: Faster Whisper transcription with CTranslate2 · GitHub](https://github.com/SYSTRAN/faster-whisper)
- [kokoro-tts · PyPI](https://pypi.org/project/kokoro-tts/)

## Prompt:
8/7/2026, 10:31:04 AM

i am confsed, what is the script I should use?

## Response:
8/7/2026, 10:31:07 AM

Use **one Python script** for now. It will do exactly this:

- Hold **Right Ctrl** → stop any current speech and start recording.
- Release **Right Ctrl** → transcribe with `faster-whisper` on your GPU.
- Type the result into the currently focused OpenCode terminal.
- You can add OpenCode → TTS afterward. Don’t start with the plugin/socket architecture yet.

Install the dependencies:

```bash
sudo apt install wtype python3-venv portaudio19-dev

mkdir -p ~/.local/share/opencode-voice
cd ~/.local/share/opencode-voice

python3 -m venv .venv
source .venv/bin/activate

pip install faster-whisper sounddevice numpy evdev
```

Add yourself to the Linux `input` group so the script can see keyboard events:

```bash
sudo usermod -aG input "$USER"
```

Then **log out and back in**.

Create:

```bash
nano ~/.local/share/opencode-voice/voice.py
```

Paste this complete script:

```python
#!/usr/bin/env python3

import subprocess
import tempfile
import threading
import os

import numpy as np
import sounddevice as sd
from evdev import InputDevice, ecodes, list_devices
from faster_whisper import WhisperModel

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

SAMPLE_RATE = 16000
PTT_KEY = ecodes.KEY_RIGHTCTRL

MODEL_NAME = "large-v3"

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

def audio_callback(indata, frames_count, time_info, status):
    if status:
        print(status)

    if recording:
        frames.append(indata.copy())

def start_recording():
    global recording, frames, stream

    if recording:
        return

    # Later, if TTS is running, we'll stop it here.
    subprocess.run(
        ["pkill", "-f", "kokoro-tts"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

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
# Inject transcription into OpenCode
# ------------------------------------------------------------

def type_into_opencode(text):
    subprocess.run(
        [
            "wtype",
            "--",
            text,
        ]
    )

# ------------------------------------------------------------
# Keyboard
# ------------------------------------------------------------

def find_keyboard():
    for path in list_devices():
        try:
            dev = InputDevice(path)
            caps = dev.capabilities()

            if ecodes.EV_KEY not in caps:
                continue

            if PTT_KEY in caps[ecodes.EV_KEY]:
                print(f"Keyboard: {dev.name}")
                return dev

        except PermissionError:
            continue

    raise RuntimeError(
        "Could not find a keyboard containing Right Ctrl.\n"
        "Check that your user is in the 'input' group."
    )

def keyboard_loop():
    dev = find_keyboard()

    print()
    print("READY")
    print("Hold Right Ctrl to talk.")
    print("Release Right Ctrl to transcribe.")
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
```

Then run:

```bash
source ~/.local/share/opencode-voice/.venv/bin/activate

python ~/.local/share/opencode-voice/voice.py
```

You should see:

```text
Loading Whisper large-v3 on CUDA...
Model loaded.
Keyboard: ...

READY
Hold Right Ctrl to talk.
Release Right Ctrl to transcribe.
```

Now open OpenCode in another terminal and leave its prompt focused.

Hold Right Ctrl and say:

> Find where the vLLM server URL is configured.

Release Right Ctrl.

After transcription, the text should appear directly in OpenCode:

```text
Find where the vLLM server URL is configured.
```

It **does not press Enter automatically**, intentionally. You can inspect the transcription and then press Enter yourself.

### The setup, for now

Forget about Unix sockets and OpenCode plugins until this works:

```text
Right Ctrl
    ↓
microphone
    ↓
faster-whisper large-v3 / CUDA
    ↓
wtype
    ↓
OpenCode prompt
```

Once this exact script works on your machine, the next change is small: add Kokoro so OpenCode's completed answers are spoken aloud, while pressing Right Ctrl immediately interrupts the speech.

## Prompt:
8/7/2026, 10:35:55 AM

I dont get any output. THe previous one with signals worked. 
(.venv) o@owl: ~/.local/share/opencode-voice $ python ~/.local/share/opencode-voice/voice.py
Loading Whisper large-v3 on CUDA...
Model loaded.
Keyboard: Microsoft Microsoft® 2.4GHz Transceiver v7.0 Consumer Control

READY
Hold Right Ctrl to talk.
Release Right Ctrl to transcribe.

## Response:
8/7/2026, 10:36:00 AM

The script found the **wrong evdev device**:

```text
Microsoft Microsoft® 2.4GHz Transceiver v7.0 Consumer Control
```

That is typically the multimedia/consumer-control interface, not the actual keyboard interface. So it never receives your Right Ctrl press.

Change `find_keyboard()` so it requires ordinary keyboard keys as well as Right Ctrl.

Replace this:

```python
def find_keyboard():
    for path in list_devices():
        try:
            dev = InputDevice(path)
            caps = dev.capabilities()

            if ecodes.EV_KEY not in caps:
                continue

            if PTT_KEY in caps[ecodes.EV_KEY]:
                print(f"Keyboard: {dev.name}")
                return dev

        except PermissionError:
            continue
```

with:

```python
def find_keyboard():
    for path in list_devices():
        try:
            dev = InputDevice(path)
            caps = dev.capabilities()

            if ecodes.EV_KEY not in caps:
                continue

            keys = caps[ecodes.EV_KEY]

            # Require it to look like an actual keyboard,
            # not a Consumer Control / multimedia interface.
            required_keys = [
                ecodes.KEY_A,
                ecodes.KEY_Z,
                ecodes.KEY_SPACE,
                PTT_KEY,
            ]

            if all(key in keys for key in required_keys):
                print(f"Keyboard: {dev.path}  {dev.name}")
                return dev

        except PermissionError:
            continue

    raise RuntimeError("No suitable keyboard found")
```

Then rerun:

```bash
python ~/.local/share/opencode-voice/voice.py
```

You ideally want something more like:

```text
Keyboard: /dev/input/event5  Microsoft Microsoft® 2.4GHz Transceiver v7.0
```

and **not**:

```text
Consumer Control
```

### Verify the keyboard first

You can also quickly see what evdev devices Python finds:

```bash
python - <<'PY'
from evdev import InputDevice, list_devices

for path in list_devices():
    d = InputDevice(path)
    print(path, ":", d.name)
PY
```

You'll probably see several Microsoft interfaces, something like:

```text
/dev/input/event3 : Microsoft Microsoft® 2.4GHz Transceiver v7.0
/dev/input/event4 : Microsoft Microsoft® 2.4GHz Transceiver v7.0 Consumer Control
/dev/input/event5 : Microsoft Microsoft® 2.4GHz Transceiver v7.0 System Control
```

The first one is generally the actual keyboard.

You can verify it interactively with:

```bash
sudo evtest
```

Select the normal Microsoft keyboard device and press Right Ctrl. You should see something equivalent to:

```text
EV_KEY KEY_RIGHTCTRL 1
EV_KEY KEY_RIGHTCTRL 0
```

If so, the revised script above will use the correct device.

The fact that your earlier **signal-based version worked** is useful: Whisper/audio transcription is probably fine. The failure is almost certainly just the new global-keyboard detection selecting `Consumer Control`.

## Prompt:
8/7/2026, 10:38:55 AM

it is finding Keyboard: /dev/input/event6  Microsoft Microsoft® 2.4GHz Transceiver v7.0 Consumer Control

but 

python - <<'PY'

> from evdev import InputDevice, list\_devices
>
> for path in list\_devices():
> d = InputDevice(path)
> print(path, ":", d.name)
> PY
> /dev/input/event9 : USB V7 AUDIO USB V7 AUDIO Consumer Control
> /dev/input/event8 : USB V7 AUDIO USB V7 AUDIO
> /dev/input/event18 : HDA Intel PCH Front Headphone
> /dev/input/event17 : HDA Intel PCH Line Out
> /dev/input/event16 : HDA Intel PCH Rear Mic
> /dev/input/event15 : HDA Intel PCH Front Mic
> /dev/input/event14 : HDA NVidia HDMI/DP,pcm=9
> /dev/input/event13 : HDA NVidia HDMI/DP,pcm=8
> /dev/input/event12 : HDA NVidia HDMI/DP,pcm=7
> /dev/input/event11 : HDA NVidia HDMI/DP,pcm=3
> /dev/input/event10 : Dell WMI hotkeys
> /dev/input/event7 : Microsoft Microsoft® 2.4GHz Transceiver v7.0 System Control
> /dev/input/event6 : Microsoft Microsoft® 2.4GHz Transceiver v7.0 Consumer Control
> /dev/input/event5 : Microsoft Microsoft® 2.4GHz Transceiver v7.0 Consumer Control
> /dev/input/event4 : Microsoft Microsoft® 2.4GHz Transceiver v7.0 Mouse
> /dev/input/event3 : Microsoft Microsoft® 2.4GHz Transceiver v7.0
> /dev/input/event2 : AT Translated Set 2 keyboard
> /dev/input/event1 : Power Button
> /dev/input/event0 : Sleep Button

## Response:
8/7/2026, 10:38:58 AM

Use `/dev/input/event3`. That is the actual Microsoft keyboard interface.

The easiest fix is to **stop auto-detecting** and hard-code the device.

Change:

```python
def find_keyboard():
    ...
```

to:

```python
def find_keyboard():
    path = "/dev/input/event3"
    dev = InputDevice(path)

    print(f"Keyboard: {dev.path}  {dev.name}")
    return dev
```

So the relevant part becomes:

```python
def find_keyboard():
    path = "/dev/input/event3"

    dev = InputDevice(path)

    print(f"Keyboard: {dev.path}  {dev.name}")
    return dev

def keyboard_loop():
    dev = find_keyboard()

    print()
    print("READY")
    print("Hold Right Ctrl to talk.")
    print("Release Right Ctrl to transcribe.")
    print()

    for event in dev.read_loop():

        if event.type != ecodes.EV_KEY:
            continue

        if event.code != PTT_KEY:
            continue

        if event.value == 1:
            print("PTT DOWN")
            start_recording()

        elif event.value == 0:
            print("PTT UP")

            threading.Thread(
                target=stop_recording,
                daemon=True,
            ).start()
```

I added:

```text
PTT DOWN
PTT UP
```

so you can immediately tell whether keyboard events are working.

Then run:

```bash
python ~/.local/share/opencode-voice/voice.py
```

Press Right Ctrl. You should see:

```text
PTT DOWN
Listening...
```

Release:

```text
PTT UP
Transcribing...
You: whatever you said
```

If you **don't** see `PTT DOWN`, verify the key code directly:

```bash
sudo evtest /dev/input/event3
```

Then press Right Ctrl. You want to see:

```text
KEY_RIGHTCTRL
```

If that appears, `/dev/input/event3` is definitely correct.

One caveat: `/dev/input/event3` can change after reboot or reconnecting the receiver. Once this is working, I can show you a better version that identifies the correct Microsoft keyboard by capabilities while explicitly excluding `Consumer Control`, `System Control`, and `Mouse`.

## Prompt:
8/7/2026, 10:40:04 AM

Loading Whisper large-v3 on CUDA...
Model loaded.
Keyboard: /dev/input/event3  Microsoft Microsoft® 2.4GHz Transceiver v7.0
READY
Hold Right Ctrl to talk.
Release Right Ctrl to transcribe.
Listening...
Transcribing...
You: Testing testing
Exception in thread Thread-1 (stop\_recording):
Traceback (most recent call last):
File "/usr/lib/python3.12/threading.py", line 1073, in \_bootstrap\_inner
self.run()
File "/usr/lib/python3.12/threading.py", line 1010, in run
self.\_target(\*self.\_args, \*\*self.\_kwargs)
File "/home/o/.local/share/opencode-voice/voice.py", line 100, in stop\_recording
transcribe(audio)
File "/home/o/.local/share/opencode-voice/voice.py", line 145, in transcribe
type\_into\_opencode(text)
File "/home/o/.local/share/opencode-voice/voice.py", line 159, in type\_into\_opencode
subprocess.run(
File "/usr/lib/python3.12/subprocess.py", line 548, in run
with Popen(\*popenargs, \*\*kwargs) as process:
^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/usr/lib/python3.12/subprocess.py", line 1026, in **init**
self.\_execute\_child(args, executable, preexec\_fn, close\_fds,
File "/usr/lib/python3.12/subprocess.py", line 1955, in \_execute\_child
raise child\_exception\_type(errno\_num, err\_msg, err\_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'wtype'

## Response:
8/7/2026, 10:40:06 AM

Good — the hard parts are working. Recording and GPU transcription are fine. The only failure is:

```text
FileNotFoundError: ... 'wtype'
```

So `wtype` is not installed.

Install it:

```bash
sudo apt install wtype
```

Then verify:

```bash
which wtype
```

You should get something like:

```text
/usr/bin/wtype
```

Then rerun your voice script.

If `apt` says `wtype` is unavailable, tell me whether you are on **Wayland or X11** with:

```bash
echo $XDG_SESSION_TYPE
```

If it says `wayland`, we can use `wtype`. If it says `x11`, I’ll switch the script to `xdotool` instead.

## Prompt:
8/7/2026, 10:40:43 AM

Loading Whisper large-v3 on CUDA...
Model loaded.
Keyboard: /dev/input/event3  Microsoft Microsoft® 2.4GHz Transceiver v7.0

READY
Hold Right Ctrl to talk.
Release Right Ctrl to transcribe.

Listening...
Transcribing...
You: Testing, testing.
Wayland connection failed

## Response:
8/7/2026, 10:40:47 AM

That means transcription is still working; the only broken piece is text injection.

`wtype` only works when it can connect to a Wayland compositor. Check your session first:

```bash
echo "session=$XDG_SESSION_TYPE"
echo "wayland=$WAYLAND_DISPLAY"
echo "display=$DISPLAY"
```

If you see something like:

```text
session=x11
wayland=
display=:0
```

then use `xdotool` instead:

```bash
sudo apt install xdotool
```

and replace your `type_into_opencode()` function with:

```python
def type_into_opencode(text):
    subprocess.run(
        ["xdotool", "type", "--clearmodifiers", "--delay", "1", text],
        check=False,
    )
```

If you are actually on Wayland but `wtype` still says `Wayland connection failed`, run:

```bash
echo "$WAYLAND_DISPLAY"
echo "$XDG_RUNTIME_DIR"
```

because `wtype` needs both environment variables from the graphical login session.

### Better: make the script handle both automatically

Replace `type_into_opencode()` with:

```python
def type_into_opencode(text):
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
```

Make sure you have both installed:

```bash
sudo apt install wtype xdotool
```

Then rerun:

```bash
python ~/.local/share/opencode-voice/voice.py
```

Your current status is actually good:

```text
microphone       ✓
Right Ctrl       ✓
CUDA Whisper     ✓
transcription    ✓
text injection   ✗
```

So we only need to choose the correct display backend. If you paste the output of the three `echo` commands above, I can tell you exactly which injector you should use.

## Prompt:
8/7/2026, 10:43:21 AM

works, now what?

## Response:
8/7/2026, 10:43:23 AM

Next, add **talk-back**. Keep the working STT script unchanged and bolt on TTS as a separate step.

The simplest path is Kokoro. Install it in the same venv:

```bash
source ~/.local/share/opencode-voice/.venv/bin/activate
pip install kokoro-tts
```

Test speech first:

```bash
echo "Voice output is working." | kokoro-tts - --stream
```

If that speaks correctly, create:

```bash
nano ~/.local/share/opencode-voice/speak.sh
```

with:

```bash
#!/bin/bash
set -e

PIDFILE=/tmp/opencode-tts.pid

cleanup() {
    rm -f "$PIDFILE"
}

trap cleanup EXIT INT TERM

echo $$ > "$PIDFILE"

exec ~/.local/share/opencode-voice/.venv/bin/kokoro-tts \
    - \
    --stream
```

Then:

```bash
chmod +x ~/.local/share/opencode-voice/speak.sh
```

Now test:

```bash
echo "OpenCode can now talk back." | ~/.local/share/opencode-voice/speak.sh
```

Your existing `voice.py` already has this behavior:

```python
subprocess.run(
    ["pkill", "-f", "kokoro-tts"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
```

So pressing Right Ctrl while it is speaking will stop the speech. That gives you basic **barge-in** immediately.

The next part is connecting OpenCode's assistant replies to `speak.sh`. I recommend doing that with a tiny OpenCode plugin rather than scraping terminal output. The plugin should speak only the assistant's final natural-language summary, not code blocks, diffs, tool output, or logs.

So the architecture becomes:

```text
you speak
  ↓
Whisper
  ↓
OpenCode
  ↓
assistant reply
  ↓
OpenCode plugin
  ↓
Kokoro
  ↓
speakers
```

If you want, I can give you the exact `~/.config/opencode/plugins/voice.ts` file next.

## Prompt:
8/7/2026, 10:45:01 AM

this is what i have now

[Attachment: voice.ts]

## Response:
8/7/2026, 10:45:03 AM

> **Searching the web**
>
> [Плагины | OpenCode](https://opencode.ai/docs/plugins/)
> [Plugins | OpenCode](https://dev.opencode.ai/docs/plugins/)
>
> **Searched 2 websites**
>
> 
>
> Worked for 7s

Yes - this `voice.ts` is a reasonable starting point. `voice.ts` OpenCode currently supports both `message.part.updated` and `session.idle`, so the overall event strategy is valid. ([OpenCode](https://opencode.ai/docs/plugins/?utm_source=chatgpt.com))

I would make **one important correction before testing TTS**: your code currently does this:

```ts
accumulated = part.text
```

That means each event replaces the previous text. Depending on how OpenCode emits updates, you may end up speaking only the last chunk. Change it to append:

```ts
accumulated += part.text
```

So this section becomes:

```ts
if (event.type === "message.part.updated") {
  const part = (event as any).properties?.part

  if (
    part?.type === "text" &&
    typeof part.text === "string"
  ) {
    accumulated += part.text
  }
}
```

However, there is a second possibility: OpenCode may send the **complete current text** in every `message.part.updated` event rather than only the new delta. In that case, `+=` would duplicate everything. The official plugin documentation lists the event but doesn't specify that payload behavior. ([OpenCode](https://opencode.ai/docs/plugins/?utm_source=chatgpt.com))

So I recommend testing your current plugin **before changing the accumulation behavior**.

First make `speak.sh` something trivially testable:

```bash
#!/bin/bash
cat >> /tmp/opencode-spoken.txt
```

Then:

```bash
chmod +x ~/.local/share/opencode-voice/speak.sh
rm -f /tmp/opencode-spoken.txt
```

Start OpenCode, ask:

```text
Say exactly: This is a voice test.
```

After the answer finishes:

```bash
cat /tmp/opencode-spoken.txt
```

If you get:

```text
This is a voice test.
```

then your existing:

```ts
accumulated = part.text
```

is correct, and **do not change it**.

If you get only:

```text
test.
```

or another final fragment, then change it to:

```ts
accumulated += part.text
```

Once that test works, replace `speak.sh` with the actual Kokoro command. This separates the two problems cleanly: first prove **OpenCode → plugin → shell script**, then introduce TTS.

---

**Sources:**

- [Плагины | OpenCode](https://opencode.ai/docs/plugins/?utm_source=chatgpt.com)

## Prompt:
8/7/2026, 10:49:08 AM

voice.ts works. now what?

## Response:
8/7/2026, 10:49:09 AM

> **Searching kokoro-tts PyPI CLI --stream voice 2026**
>
> [kokoro-tts · PyPI](https://pypi.org/project/kokoro-tts/)
> [Plugins | OpenCode](https://dev.opencode.ai/docs/plugins/)
> [GitHub - nazdridoy/kokoro-tts: A CLI text-to-speech tool using the Kokoro model, supporting multiple languages, voices (with blending), and various input formats including EPUB books and PDF documents. · GitHub](https://github.com/nazdridoy/kokoro-tts)
> [OpenCode Plugins: Extend with TypeScript & Hooks - OpenCode Docs](https://open-code.ai/en/docs/plugins)
> [Plugins - OpenCode Docs | OpenCode Tutorial](https://opencode-tutorial.com/en/docs/plugins)
> [piwheels - kokoro-tts](https://www.piwheels.org/project/kokoro-tts/)
> [run.py · echodict/kokoro-tts at main](https://huggingface.co/datasets/echodict/kokoro-tts/blob/main/run.py)
> [I created a Text-to-speach plugin for opencode](https://www.reddit.com/r/opencode/comments/1szep3t/i_created_a_texttospeach_plugin_for_opencode/)
> [T5Gemma-TTS Technical Report](https://arxiv.org/abs/2604.01760)
>
> **Searched 9 websites**
>
> 
>
> Worked for 7s

Since `voice.ts` is working, the next step is simply to make `speak.sh` call Kokoro and confirm OpenCode speaks its completed replies. Your plugin already invokes `~/.local/share/opencode-voice/speak.sh` on `session.idle`. `voice.ts` OpenCode still exposes the `message.part.updated` and `session.idle` plugin events your implementation relies on. ([OpenCode](https://dev.opencode.ai/docs/plugins/?utm_source=chatgpt.com))

Install Kokoro into the same venv:

```bash
source ~/.local/share/opencode-voice/.venv/bin/activate
pip install kokoro-tts
```

The current `kokoro-tts` package supports streaming output and selectable voices. ([PyPI](https://pypi.org/project/kokoro-tts/?utm_source=chatgpt.com)) Test it directly first:

```bash
echo "OpenCode can now talk to me." | kokoro-tts - --stream --voice af_heart
```

If you hear that, make `~/.local/share/opencode-voice/speak.sh`:

```bash
#!/bin/bash

set -e

exec ~/.local/share/opencode-voice/.venv/bin/kokoro-tts \
    - \
    --stream \
    --voice af_heart
```

Then:

```bash
chmod +x ~/.local/share/opencode-voice/speak.sh
```

Test the exact script:

```bash
echo "Testing OpenCode voice output." \
  | ~/.local/share/opencode-voice/speak.sh
```

If that works, restart OpenCode and ask it something short, for example:

```text
What is 2 plus 2? Answer in one sentence.
```

When OpenCode becomes idle, your existing plugin should send the assistant text to `speak.sh`, and you should hear the reply.

### Then fix interruption

Your `voice.py` already tries to do:

```python
subprocess.run(
    ["pkill", "-f", "kokoro-tts"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
```

when you press Right Ctrl.

That means the desired behavior should already be:

```text
OpenCode speaking
       ↓
press Right Ctrl
       ↓
Kokoro stops
       ↓
microphone starts
       ↓
you speak
```

So test that next. Give OpenCode a deliberately long answer:

```text
Explain speculative decoding in ten paragraphs.
```

While it is speaking, hold Right Ctrl.

If the speech immediately stops and you see:

```text
Listening...
```

then you have functioning **push-to-talk barge-in**.

### One change I would make to `voice.ts`

Right now it will potentially read up to the last 800 characters of the entire response. `voice.ts` That can get annoying quickly with coding-agent output.

A better first version is to limit speech to about 300 characters:

```ts
const spoken =
  text.length > 300
    ? text.slice(-300)
    : text
```

Even better, after we establish that Kokoro works, I would change OpenCode so each answer ends with a dedicated marker such as:

```text
<voice>
The changes are complete and all tests pass.
</voice>
```

and make `voice.ts` speak **only that section**.

That gives you:

```text
screen:
  full answer
  code
  diffs
  logs
  technical details

speakers:
  "The changes are complete and all tests pass."
```

That is the next improvement I recommend after confirming `speak.sh` produces audio.

---

**Sources:**

- [Plugins | OpenCode](https://dev.opencode.ai/docs/plugins/?utm_source=chatgpt.com)
- [kokoro-tts · PyPI](https://pypi.org/project/kokoro-tts/?utm_source=chatgpt.com)

## Prompt:
8/7/2026, 10:57:48 AM

how to swtitch speak off/on in a session

## Response:
8/7/2026, 10:57:50 AM

Simplest is to add a per-session toggle file that `voice.ts` checks before calling TTS.

For example, use:

```text
/tmp/opencode-voice-enabled
```

When the file exists, speech is ON. When it doesn’t, speech is OFF.

Update `voice.ts` like this:

```ts
import type { Plugin } from "@opencode-ai/plugin"
import { existsSync } from "node:fs"

const TTS =
  `${process.env.HOME}/.local/share/opencode-voice/speak.sh`

const VOICE_FLAG = "/tmp/opencode-voice-enabled"

function cleanForSpeech(text: string): string {
  return text
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`[^`]+`/g, " ")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/(?:\/[\w.\-]+){2,}/g, " ")
    .replace(/https?:\/\/\S+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
}

export const VoicePlugin: Plugin = async ({
  client,
  $
}) => {

  let accumulated = ""

  return {

    event: async ({ event }) => {

      if (event.type === "message.part.updated") {
        const part = (event as any).properties?.part

        if (
          part?.type === "text" &&
          typeof part.text === "string"
        ) {
          accumulated = part.text
        }
      }

      if (event.type === "session.idle") {

        const text = cleanForSpeech(accumulated)
        accumulated = ""

        // Speech disabled
        if (!existsSync(VOICE_FLAG))
          return

        if (!text)
          return

        const spoken =
          text.length > 800
            ? text.slice(-800)
            : text

        await $`echo ${spoken} | ${TTS}`
      }
    },
  }
}
```

Then enable speech with:

```bash
touch /tmp/opencode-voice-enabled
```

Disable it with:

```bash
rm -f /tmp/opencode-voice-enabled
```

Check current state:

```bash
test -f /tmp/opencode-voice-enabled && echo ON || echo OFF
```

You can make shell aliases:

```bash
alias voice-on='touch /tmp/opencode-voice-enabled'
alias voice-off='rm -f /tmp/opencode-voice-enabled'
alias voice-status='test -f /tmp/opencode-voice-enabled && echo ON || echo OFF'
```

Put those in `~/.bashrc`.

Then in any terminal:

```bash
voice-on
```

or:

```bash
voice-off
```

One caveat: `/tmp/opencode-voice-enabled` is **global across all OpenCode sessions**. If you want the toggle to apply to only one OpenCode session while another session can still speak, the better version is to key the flag by OpenCode session ID.

## Prompt:
8/7/2026, 11:03:44 AM

remove asterix-asterix from teh speech output

## Response:
8/7/2026, 11:03:46 AM

Add this to `cleanForSpeech()`:

```ts
.replace(/\*\*/g, "")
```

So your function becomes:

```ts
function cleanForSpeech(text: string): string {
  return text
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`[^`]+`/g, " ")
    .replace(/\*\*/g, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/(?:\/[\w.\-]+){2,}/g, " ")
    .replace(/https?:\/\/\S+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
}
```

That turns:

```text
**Important:** tests passed
```

into:

```text
Important: tests passed
```

before it reaches TTS.

## Prompt:
8/7/2026, 11:04:41 AM

add comments to each clealup line

## Response:
8/7/2026, 11:04:43 AM

Sure—here’s the same cleanup function with a comment explaining every transformation:

```ts
function cleanForSpeech(text: string): string {
  return text
    // Remove fenced Markdown code blocks: ``` ... ```
    .replace(/```[\s\S]*?```/g, " ")

    // Remove inline Markdown code, including its backticks: `example`
    .replace(/`[^`]+`/g, " ")

    // Remove Markdown bold markers: **important** -> important
    .replace(/\*\*/g, "")

    // Convert Markdown links to just their visible text:
    // [OpenCode](https://opencode.ai) -> OpenCode
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")

    // Remove Unix-style filesystem paths:
    // /home/user/project/file.ts -> removed
    .replace(/(?:\/[\w.\-]+){2,}/g, " ")

    // Remove HTTP and HTTPS URLs
    .replace(/https?:\/\/\S+/g, " ")

    // Collapse newlines, tabs, and repeated spaces into one space
    .replace(/\s+/g, " ")

    // Remove whitespace from the beginning and end
    .trim()
}
```

One thing I’d consider changing: your inline-code rule currently removes the **contents** too. So:

```text
Use `large-v3` for transcription.
```

becomes:

```text
Use for transcription.
```

For speech, you may prefer stripping only the backticks:

```ts
// Remove inline-code backticks but preserve the enclosed text:
// `large-v3` -> large-v3
.replace(/`([^`]+)`/g, "$1")
```

That tends to work better for technical OpenCode responses.

## Prompt:
8/7/2026, 6:45:49 PM

where is voice.ts?

## Response:
8/7/2026, 6:45:50 PM

The `voice.ts` you showed me should be installed at:

```bash
~/.config/opencode/plugins/voice.ts
```

Check it with:

```bash
ls -l ~/.config/opencode/plugins/voice.ts
```

Edit it with:

```bash
nano ~/.config/opencode/plugins/voice.ts
```

The file you uploaded to this chat is a separate copy; your working OpenCode plugin should be the one under `~/.config/opencode/plugins/`. `voice.ts`

## Prompt:
8/7/2026, 9:44:07 PM

use ~/.local/share/opencode-voice/voice.py to say a text from paste buffer

## Response:
8/7/2026, 9:44:07 PM

Yes. Since `voice.py` currently handles **speech-to-text**, I’d add a small command-line mode so it can also send clipboard text to your existing `speak.sh`.

Add this import near the top of `~/.local/share/opencode-voice/voice.py`:

```python
import sys
```

Then add this function:

```python
def speak_clipboard():
    # Read the current clipboard. Supports both Wayland and X11.
    if os.environ.get("WAYLAND_DISPLAY"):
        result = subprocess.run(
            ["wl-paste", "--no-newline"],
            capture_output=True,
            text=True,
            check=True,
        )
    else:
        result = subprocess.run(
            ["xclip", "-selection", "clipboard", "-o"],
            capture_output=True,
            text=True,
            check=True,
        )

    text = result.stdout.strip()

    if not text:
        print("Clipboard is empty.")
        return

    print(f"Speaking: {text}")

    subprocess.run(
        [os.path.expanduser(
            "~/.local/share/opencode-voice/speak.sh"
        )],
        input=text,
        text=True,
        check=True,
    )
```

Then change the bottom of `voice.py` from:

```python
if __name__ == "__main__":
    print("Loading Whisper large-v3 on CUDA...")
    print("Model loaded.")

    keyboard_loop()
```

to:

```python
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--speak-clipboard":
        speak_clipboard()
    else:
        print("Loading Whisper large-v3 on CUDA...")
        print("Model loaded.")

        keyboard_loop()
```

Install the clipboard utility. For Wayland:

```bash
sudo apt install wl-clipboard
```

For X11:

```bash
sudo apt install xclip
```

Then you can copy any text and run:

```bash
~/.local/share/opencode-voice/.venv/bin/python \
    ~/.local/share/opencode-voice/voice.py \
    --speak-clipboard
```

### One optimization

Your current script constructs `WhisperModel(...)` globally, which means even `--speak-clipboard` will unnecessarily load **large-v3 onto the GPU** before speaking.

Move this:

```python
model = WhisperModel(
    MODEL_NAME,
    device="cuda",
    compute_type="float16",
)
```

out of the global scope and initialize it only for STT. Then clipboard → TTS becomes essentially instantaneous.

Alternatively, if your only goal is **“speak whatever I copied”**, there's no reason to involve `voice.py` at all. The cleaner command is simply:

```bash
wl-paste --no-newline | ~/.local/share/opencode-voice/speak.sh
```

On X11:

```bash
xclip -selection clipboard -o | ~/.local/share/opencode-voice/speak.sh
```

**I recommend this latter approach.** You can bind that one command to a global keyboard shortcut and have copied text read aloud immediately.

## Prompt:
8/7/2026, 10:39:17 PM

reduce lattency of kokoro-tts

## Response:
8/7/2026, 10:39:19 PM

> **Searching the web**
>
> [Kokoro-TTS-Local/README.md at master · PierrunoYT/Kokoro-TTS-Local · GitHub](https://github.com/PierrunoYT/Kokoro-TTS-Local/blob/master/README.md)
> [app.py · hexgrad/Kokoro-TTS at main](https://huggingface.co/spaces/hexgrad/Kokoro-TTS/blob/main/app.py)
> [go-kokoro-tts module - github.com/chasedputnam/go-kokoro-tts - Go Packages](https://pkg.go.dev/github.com/chasedputnam/go-kokoro-tts)
> [We made significant improvements to the Kokoro TTS trainer](https://www.reddit.com/r/LocalLLaMA/comments/1sddrvz/we_made_significant_improvements_to_the_kokoro/)
> [Faster IndexTTS-2: Accelerating and Streaming Autoregressive Zero-Shot Text-to-Speech Synthesis on GPUs](https://arxiv.org/abs/2607.21042)
>
> **Searched 5 websites**
>
> 
>
> Worked for 4s

The biggest latency source in your current setup is likely **process startup**, not Kokoro inference itself. Every OpenCode reply launches:

```bash
kokoro-tts ...
```

which reloads Python, PyTorch, the Kokoro model, and the voice. With your spare VRAM, keep Kokoro **resident on the GPU** instead. The reference Kokoro implementation explicitly keeps `KModel()` loaded on CUDA and reuses the voice pipeline, which is the right architecture for low-latency interactive TTS. ([Hugging Face](https://huggingface.co/spaces/hexgrad/Kokoro-TTS/blob/main/app.py?utm_source=chatgpt.com))

I’d replace `speak.sh` with a persistent TTS daemon.

Create `~/.local/share/opencode-voice/tts_server.py`:

```python
#!/usr/bin/env python3

import socket
import torch
import sounddevice as sd

from kokoro import KModel, KPipeline

SOCKET = "/tmp/opencode-tts.sock"
VOICE = "af_heart"
SPEED = 1.1

print("Loading Kokoro on CUDA...")

model = KModel().to("cuda").eval()

pipeline = KPipeline(
    lang_code="a",
    model=False,
)

voice = pipeline.load_voice(VOICE)

print("Kokoro ready.")

def speak(text: str):
    for _, phonemes, _ in pipeline(text, VOICE, SPEED):
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

server = socket.socket(
    socket.AF_UNIX,
    socket.SOCK_STREAM,
)

try:
    import os
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
```

Install the direct Kokoro package if needed:

```bash
source ~/.local/share/opencode-voice/.venv/bin/activate

pip install kokoro sounddevice
sudo apt install espeak-ng
```

Make sure PyTorch is actually seeing your GPU:

```bash
python - <<'PY'
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name())
PY
```

You want:

```text
True
NVIDIA ...
```

CUDA-backed Kokoro is substantially preferable for latency on Linux/NVIDIA. ([GitHub](https://github.com/PierrunoYT/Kokoro-TTS-Local/blob/master/README.md?utm_source=chatgpt.com))

Then run the server once:

```bash
~/.local/share/opencode-voice/.venv/bin/python \
    ~/.local/share/opencode-voice/tts_server.py
```

Wait until:

```text
Loading Kokoro on CUDA...
Kokoro ready.
Listening on /tmp/opencode-tts.sock
```

Now change `speak.sh` to simply send text to that already-running process:

```bash
#!/bin/bash

exec socat - UNIX-CONNECT:/tmp/opencode-tts.sock
```

Install `socat`:

```bash
sudo apt install socat
chmod +x ~/.local/share/opencode-voice/speak.sh
```

Test:

```bash
echo "This should start speaking much faster." \
  | ~/.local/share/opencode-voice/speak.sh
```

The difference is architectural:

```text
CURRENT

OpenCode reply
   ↓
start Python
   ↓
import PyTorch
   ↓
load Kokoro
   ↓
load voice
   ↓
CUDA initialization
   ↓
synthesize
   ↓
audio
```

versus:

```text
RECOMMENDED

startup once:
Kokoro + voice → GPU VRAM

then every reply:

OpenCode
   ↓
Unix socket
   ↓
already-loaded Kokoro
   ↓
audio
```

That should cut a substantial amount from **time-to-first-audio**.

There are two further improvements after this.

First, don't wait for the entire OpenCode answer. Your current `voice.ts` waits until:

```ts
event.type === "session.idle"
```

So even infinitely-fast TTS cannot speak until OpenCode has finished generating. For conversational behavior, send complete sentences to Kokoro while the assistant is still streaming. A community OpenCode/Kokoro plugin takes exactly that approach and supports reading streamed assistant responses. ([Reddit](https://www.reddit.com/r/opencode/comments/1szep3t/i_created_a_texttospeach_plugin_for_opencode/?utm_source=chatgpt.com))

Second, synthesize chunks rather than a large 800-character block:

```text
"The changes are complete."
       ↓ synthesize/play immediately

"All tests now pass."
       ↓ synthesize/play

"I left one warning unchanged."
       ↓ synthesize/play
```

rather than waiting to synthesize:

```text
"The changes are complete. All tests now pass.
I left one warning unchanged..."
```

For your RTX 6000 Pro setup, **persistent CUDA Kokoro + sentence-level streaming from `voice.ts`** is the configuration I'd use. The persistent server should be the first change; then we can modify your working `voice.ts` to start talking while OpenCode is generating instead of waiting for `session.idle`.

---

**Sources:**

- [app.py · hexgrad/Kokoro-TTS at main](https://huggingface.co/spaces/hexgrad/Kokoro-TTS/blob/main/app.py?utm_source=chatgpt.com)
- [Kokoro-TTS-Local/README.md at master · PierrunoYT/Kokoro-TTS-Local · GitHub](https://github.com/PierrunoYT/Kokoro-TTS-Local/blob/master/README.md?utm_source=chatgpt.com)
- [I created a Text-to-speach plugin for opencode](https://www.reddit.com/r/opencode/comments/1szep3t/i_created_a_texttospeach_plugin_for_opencode/?utm_source=chatgpt.com)

## Prompt:
8/7/2026, 10:47:06 PM

done working  persistent CUDA Kokoro

## Response:
8/7/2026, 10:47:07 PM

Great. The next meaningful improvement is **sentence-level streaming from `voice.ts`** so Kokoro starts speaking before OpenCode finishes the whole response.

Right now your plugin waits for `session.idle`, so TTS latency includes the entire model-generation time. Instead, buffer assistant text and send each completed sentence to your persistent Kokoro socket as soon as it arrives.

I’d change `voice.ts` to this pattern:

```ts
import type { Plugin } from "@opencode-ai/plugin"

const TTS =
  `${process.env.HOME}/.local/share/opencode-voice/speak.sh`

function cleanForSpeech(text: string): string {
  return text
    // Remove fenced Markdown code blocks
    .replace(/```[\s\S]*?```/g, " ")

    // Preserve inline-code text, remove only backticks
    .replace(/`([^`]+)`/g, "$1")

    // Remove Markdown bold markers
    .replace(/\*\*/g, "")

    // Keep only the visible part of Markdown links
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")

    // Remove Unix-style filesystem paths
    .replace(/(?:\/[\w.\-]+){2,}/g, " ")

    // Remove URLs
    .replace(/https?:\/\/\S+/g, " ")

    // Collapse whitespace
    .replace(/\s+/g, " ")

    // Trim leading/trailing whitespace
    .trim()
}

export const VoicePlugin: Plugin = async ({ $ }) => {
  let previousText = ""
  let speechBuffer = ""

  async function speak(text: string) {
    const cleaned = cleanForSpeech(text)

    if (!cleaned)
      return

    // Don't await this; let OpenCode keep streaming.
    $`echo ${cleaned} | ${TTS}`.catch(() => {})
  }

  async function flushCompleteSentences() {
    // Speak complete sentences, but leave an unfinished
    // final sentence in the buffer.
    const match = speechBuffer.match(
      /^([\s\S]*[.!?])(\s+[^.!?]*)?$/
    )

    if (!match)
      return

    const complete = match[1].trim()
    const remainder = match[2]?.trim() ?? ""

    speechBuffer = remainder

    if (complete)
      await speak(complete)
  }

  return {
    event: async ({ event }) => {
      if (event.type === "message.part.updated") {
        const part = (event as any).properties?.part

        if (
          part?.type !== "text" ||
          typeof part.text !== "string"
        ) {
          return
        }

        /*
         * OpenCode commonly gives us the current full text
         * for the part, not just the newest characters.
         *
         * Extract only what was appended since the previous
         * event.
         */
        const currentText = part.text

        let delta = currentText

        if (currentText.startsWith(previousText)) {
          delta = currentText.slice(previousText.length)
        }

        previousText = currentText

        if (!delta)
          return

        speechBuffer += delta

        await flushCompleteSentences()
      }

      if (event.type === "session.idle") {
        // Speak whatever remains after the final sentence.
        const remaining = speechBuffer.trim()

        speechBuffer = ""
        previousText = ""

        if (remaining)
          await speak(remaining)
      }
    },
  }
}
```

The behavior becomes:

```text
OpenCode generates:
"The implementation is complete."
        ↓
Kokoro starts speaking immediately

OpenCode continues:
"I also fixed the failing test."
        ↓
Kokoro queues/speaks that next
```

instead of:

```text
OpenCode generates entire response
        ↓
session.idle
        ↓
Kokoro starts
```

One thing to watch: your persistent TTS server needs to **queue incoming utterances** rather than trying to play multiple socket requests simultaneously. If it currently handles one connection synchronously, you are probably already safe. If you made it threaded, we should add an explicit speech queue next.

After this, the two biggest quality upgrades are **better sentence segmentation** and **PTT cancellation that clears already-queued speech as well as stopping the current utterance**.

## Prompt:
8/7/2026, 10:52:50 PM

i want to bind recording to a differnt key, keycode 180

## Response:
8/7/2026, 10:52:52 PM

Change the PTT constant in `voice.py` from:

```python
PTT_KEY = ecodes.KEY_RIGHTCTRL
```

to:

```python
PTT_KEY = 180
```

Then your event filter can stay exactly as it is:

```python
if event.code != PTT_KEY:
    continue
```

I’d also update the status text so it doesn’t still say Right Ctrl:

```python
print("READY")
print("Hold keycode 180 to talk.")
print("Release keycode 180 to transcribe.")
```

If you want to verify that `180` is really the key you intend, run:

```bash
sudo evtest /dev/input/event3
```

press that key, and look for:

```text
code 180
```

Then restart:

```bash
python ~/.local/share/opencode-voice/voice.py
```

That’s all you need.

## Prompt:
8/7/2026, 10:57:08 PM

weird, xev shows keycode 180, evtest shows nothing

## Response:
8/7/2026, 10:57:09 PM

That is not actually inconsistent. `xev` reports an **X11 keycode**, while `evtest` reports the **Linux input-event key code** from `/dev/input/event*`. They are different numbering systems.

So `180` from `xev` is probably not the value you should put into:

```python
event.code
```

in your `evdev` script.

First find which physical input device receives that key. Run:

```bash
sudo evtest
```

and try the likely devices one by one, especially:

```text
/dev/input/event3   Microsoft ... Transceiver
/dev/input/event2   AT Translated Set 2 keyboard
/dev/input/event10  Dell WMI hotkeys
```

Press the special key on each device. One of them may produce something like:

```text
Event: type 1 (EV_KEY), code 148 (KEY_PROG1), value 1
Event: type 1 (EV_KEY), code 148 (KEY_PROG1), value 0
```

Then use that **evdev code**, preferably symbolically:

```python
PTT_KEY = ecodes.KEY_PROG1
```

rather than the X11 `180`.

If **none** of the `/dev/input/event*` devices show anything, then the key is likely being synthesized higher in the stack—e.g. by XKB, your desktop environment, or a vendor hotkey daemon. In that case `evdev` cannot bind it directly, even though `xev` sees it.

A useful diagnostic is:

```bash
xev | grep -E 'keycode|keysym'
```

Press the key and paste the resulting line, for example:

```text
keycode 180 (keysym 0x1008ff...)
```

The **keysym name** is more informative than the number. From that I can tell you whether to bind it through evdev, X11, or a desktop shortcut instead.

## Prompt:
8/7/2026, 11:01:54 PM

now we have two python scripts running. any way to make it into a service?

## Response:
8/7/2026, 11:01:57 PM

Yes. The clean way is to run both Python processes as **systemd user services**.

Assuming you currently have:

```text
~/.local/share/opencode-voice/voice.py
~/.local/share/opencode-voice/tts_server.py
```

create:

```bash
mkdir -p ~/.config/systemd/user
```

For STT/PTT, create:

```bash
nano ~/.config/systemd/user/opencode-voice.service
```

with:

```ini
[Unit]
Description=OpenCode Voice STT/PTT
After=graphical-session.target

[Service]
Type=simple
ExecStart=%h/.local/share/opencode-voice/.venv/bin/python %h/.local/share/opencode-voice/voice.py
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
```

For Kokoro:

```bash
nano ~/.config/systemd/user/opencode-tts.service
```

with:

```ini
[Unit]
Description=OpenCode Persistent Kokoro TTS
After=graphical-session.target

[Service]
Type=simple
ExecStart=%h/.local/share/opencode-voice/.venv/bin/python %h/.local/share/opencode-voice/tts_server.py
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
```

Then reload systemd:

```bash
systemctl --user daemon-reload
```

Enable both at login:

```bash
systemctl --user enable --now opencode-voice.service
systemctl --user enable --now opencode-tts.service
```

Check status:

```bash
systemctl --user status opencode-voice.service
systemctl --user status opencode-tts.service
```

Logs:

```bash
journalctl --user -u opencode-voice.service -f
```

and:

```bash
journalctl --user -u opencode-tts.service -f
```

To restart after editing a script:

```bash
systemctl --user restart opencode-voice.service
systemctl --user restart opencode-tts.service
```

To stop:

```bash
systemctl --user stop opencode-voice.service
systemctl --user stop opencode-tts.service
```

One important point: because `voice.py` reads `/dev/input/event*`, your user still needs to be in the `input` group. The systemd user service runs as your user, so the permission setup you already made continues to apply.

For the TTS service, if it needs your graphical/audio environment and fails under systemd, add this under `[Service]`:

```ini
Environment=XDG_RUNTIME_DIR=/run/user/%U
```

Usually PipeWire works fine in a user service without extra configuration.

I’d keep them as **two separate services**, not merge them. STT and TTS have different failure modes and restart independently, which is much easier to debug.

## Prompt:
8/7/2026, 11:04:26 PM

add startup directory to %h/.local/share/opencode-voice

## Response:
8/7/2026, 11:04:28 PM

Add `WorkingDirectory=%h/.local/share/opencode-voice` to each service.

For STT:

```ini
[Unit]
Description=OpenCode Voice STT/PTT
After=graphical-session.target

[Service]
Type=simple
WorkingDirectory=%h/.local/share/opencode-voice
ExecStart=%h/.local/share/opencode-voice/.venv/bin/python %h/.local/share/opencode-voice/voice.py
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
```

For TTS:

```ini
[Unit]
Description=OpenCode Persistent Kokoro TTS
After=graphical-session.target

[Service]
Type=simple
WorkingDirectory=%h/.local/share/opencode-voice
ExecStart=%h/.local/share/opencode-voice/.venv/bin/python %h/.local/share/opencode-voice/tts_server.py
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
```

Then reload and restart:

```bash
systemctl --user daemon-reload
systemctl --user restart opencode-voice.service opencode-tts.service
```

Verify the effective setting with:

```bash
systemctl --user show opencode-voice.service -p WorkingDirectory
systemctl --user show opencode-tts.service -p WorkingDirectory
```

You should see:

```text
WorkingDirectory=/home/o/.local/share/opencode-voice
```



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)