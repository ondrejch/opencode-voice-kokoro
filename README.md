# OpenCode Voice (Kokoro)

Push-to-talk voice control for [OpenCode](https://opencode.ai) on Linux.
Speak prompts into your terminal, hear OpenCode's replies aloud.

```
microphone → faster-whisper (GPU) → OpenCode prompt
OpenCode reply → Kokoro TTS (GPU) → speakers
```

**Features**
- Hold a key to talk, release to transcribe (push-to-talk)
- GPU-accelerated STT (`faster-whisper` large-v3) and TTS (Kokoro)
- Barge-in: pressing the PTT key instantly stops TTS speech
- Markdown-aware text cleaning before TTS
- Persistent Kokoro daemon to avoid per-reply model startup
- Runs as systemd user services, starts at login

## Requirements

- Linux (Ubuntu 24.04 tested)
- NVIDIA GPU with CUDA drivers (for Whisper + Kokoro on GPU)
- OpenCode installed
- Python 3.12+
- `ffmpeg`, `portaudio19-dev`
- `wtype` (Wayland) or `xdotool` (X11) for text injection
- `socat` for TTS socket communication
- `espeak-ng` (Kokoro dependency)

## Installation

### Quick install (recommended)

```bash
git clone https://github.com/<your-user>/opencode-voice-kokoro.git
cd opencode-voice-kokoro
./install.sh
```

This installs system packages, creates a Python venv, copies scripts,
installs the OpenCode plugin, and enables systemd services. Pass
`--skip-system`, `--skip-venv`, `--skip-plugin`, or `--skip-services`
to skip individual steps.

### Post-install: configure your PTT key

Edit `~/.local/share/opencode-voice/voice.py` and set `PTT_PATH`
and `PTT_KEY` to match your keyboard. Use the included utility:

```bash
~/.local/share/opencode-voice/.venv/bin/python \
    ~/.local/share/opencode-voice/find_ptt_key.py
```

The repo keeps two example pairs from the author's keyboard;
only the lower pair is active. Replace them with your own values.
See **Finding your key** below for details.

### Enable voice output

Voice output is **off** by default. Enable with:

```bash
touch /tmp/opencode-voice-enabled
```

Optional: add aliases to `~/.bashrc`:

```bash
alias voice-on='touch /tmp/opencode-voice-enabled'
alias voice-off='rm -f /tmp/opencode-voice-enabled'
alias voice-status='test -f /tmp/opencode-voice-enabled && echo ON || echo OFF'
```

### Manual installation

<details>
<summary>Click to expand manual steps</summary>

#### 1. System packages

```bash
sudo apt install ffmpeg pipewire-audio portaudio19-dev \
    python3.12-venv wtype xdotool socat espeak-ng
```

#### 2. Clone and set up Python environment

```bash
git clone https://github.com/<your-user>/opencode-voice-kokoro.git
cd opencode-voice-kokoro

INSTALL_DIR="$HOME/.local/share/opencode-voice"
mkdir -p "$INSTALL_DIR"

cp scripts/voice.py scripts/tts_server.py scripts/speak.sh \
    scripts/find_ptt_key.py "$INSTALL_DIR"/
chmod +x "$INSTALL_DIR"/speak.sh "$INSTALL_DIR"/find_ptt_key.py

python3.12 -m venv "$INSTALL_DIR/.venv"
source "$INSTALL_DIR/.venv/bin/activate"
pip install -r requirements.txt
```

#### 3. Install the OpenCode plugin

```bash
mkdir -p ~/.config/opencode/plugins
cp plugin/voice.ts ~/.config/opencode/plugins/voice.ts
```

#### 4. Keyboard access

```bash
sudo usermod -aG input "$USER"
```

Then **log out and back in**.

#### 5. Enable systemd services

```bash
cp systemd/*.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now opencode-voice.service opencode-tts.service
```

</details>

## Running

### Quick test

```bash
# Terminal 1: start TTS daemon
source ~/.local/share/opencode-voice/.venv/bin/activate
python ~/.local/share/opencode-voice/tts_server.py

# Terminal 2: test speech
echo "Hello, this is a test." | ~/.local/share/opencode-voice/speak.sh

# Terminal 3: start STT daemon
source ~/.local/share/opencode-voice/.venv/bin/activate
python ~/.local/share/opencode-voice/voice.py
```

Hold your configured PTT key, speak, release. The transcription should
appear in the focused terminal.

### As systemd services (recommended)

```bash
cp systemd/opencode-voice.service systemd/opencode-tts.service \
    ~/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable --now opencode-voice.service opencode-tts.service
```

Check status:

```bash
systemctl --user status opencode-voice.service opencode-tts.service
```

View logs:

```bash
journalctl --user -u opencode-voice.service -f
journalctl --user -u opencode-tts.service -f
```

## Finding your PTT key

Run the included utility:

```bash
source ~/.local/share/opencode-voice/.venv/bin/activate
python ~/.local/share/opencode-voice/find_ptt_key.py
```

It lists all input devices, then prints the `PTT_PATH` and `PTT_KEY`
values as soon as you press a key.  Example output:

```
Device: /dev/input/event6  Microsoft ... Consumer Control
  PTT_PATH = "/dev/input/event6"
  PTT_KEY  = ecodes.KEY_HOMEPAGE
  # or numerically: PTT_KEY = 103
```

Paste those two lines into `~/.local/share/opencode-voice/voice.py`.

The two pairs already in `voice.py` are just examples from the author's
keyboard. Replace them with your own values.

If your key does not appear but shows in `xev`, it is an X11-only
keycode and cannot be used with this evdev-based approach.

## Architecture

```
voice.py          Push-to-talk daemon. Records audio on key-hold,
                  transcribes with Whisper on key-release, injects
                  text via wtype/xdotool. Signals tts_server.py on
                  key-press to stop current speech for barge-in.

tts_server.py     Persistent Kokoro TTS server. Keeps the model
                  loaded on CUDA, listens on Unix socket
                  /tmp/opencode-tts.sock for text, plays audio.

speak.sh          Thin wrapper: sends stdin to tts_server.py via socat.

voice.ts          OpenCode plugin. Listens for assistant messages,
                  cleans Markdown, sends text to speak.sh on
                  session.idle. Toggle via /tmp/opencode-voice-enabled.
```

## TTS configuration

In `scripts/tts_server.py`:

| Variable | Default     | Description                  |
|----------|-------------|------------------------------|
| VOICE    | af_heart    | Kokoro voice (see below)     |
| SPEED    | 1.1         | Speech speed multiplier      |
| SOCKET   | /tmp/opencode-tts.sock | Unix socket path       |

Available Kokoro voices: `af_heart`, `af_sarah`, `am_michael`,
`am_onyx`, and others. Run `kokoro-tts --help` for the full list.

## Voice cleaning

The OpenCode plugin strips Markdown formatting before sending text to
TTS: code blocks, backticks, bold/italic markers, URLs, paths,
headings, lists, and blockquotes. The goal is natural-sounding speech
from technical agent output.

## Troubleshooting

**"Wayland connection failed"** — Make sure the script runs in your
graphical session, not from a TTY or SSH. The `WAYLAND_DISPLAY` and
`XDG_RUNTIME_DIR` environment variables must be set.

**"Permission denied" on /dev/input/event\*** — Add your user to the
`input` group and log out/in.

**TTS service fails under systemd** — Add
`Environment=XDG_RUNTIME_DIR=/run/user/%U` to the service file.

**"No such file or directory: wtype"** — Install with
`sudo apt install wtype` (Wayland) or `sudo apt install xdotool`
(X11).

**Kokoro model download** — On first run, Kokoro will download the
model (~300 MB) to `~/.cache/huggingface/`.

## Testing

Python tests (no GPU needed):

```bash
pip install -r requirements-dev.txt
pytest tests/
```

TypeScript tests:

```bash
npm install
npm test
```

## License

This project is licensed under the [MIT License](LICENSE).
