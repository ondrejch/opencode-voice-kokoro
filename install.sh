#!/usr/bin/env bash
# Install script for OpenCode Voice (Kokoro)
# Usage: ./install.sh [--skip-system] [--skip-venv] [--skip-plugin] [--skip-grok-hook] [--skip-services]
set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/share/opencode-voice}"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[+]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
err()   { echo -e "${RED}[-]${NC} $*" >&2; }

SKIP_SYSTEM=0
SKIP_VENV=0
SKIP_PLUGIN=0
SKIP_GROK_HOOK=0
SKIP_SERVICES=0
PLUGIN_VARIANT="auto"  # auto | v1 | v2

for arg in "$@"; do
  case "$arg" in
    --skip-system)    SKIP_SYSTEM=1 ;;
    --skip-venv)      SKIP_VENV=1 ;;
    --skip-plugin)    SKIP_PLUGIN=1 ;;
    --skip-grok-hook) SKIP_GROK_HOOK=1 ;;
    --skip-services)  SKIP_SERVICES=1 ;;
    --v1)             PLUGIN_VARIANT="v1" ;;
    --v2)             PLUGIN_VARIANT="v2" ;;
    --help|-h)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --skip-system    Skip system package installation (requires sudo)"
      echo "  --skip-venv      Skip Python venv creation (use existing)"
      echo "  --skip-plugin    Skip OpenCode plugin installation"
      echo "  --skip-grok-hook Skip Grok Build Stop-hook installation"
      echo "  --skip-services  Skip systemd service installation"
      echo "  --v1             Install the OpenCode V1 plugin layout (voice.ts + kokoro/)"
      echo "  --v2             Install the OpenCode V2 plugin layout (voice/ dir, id: voice-kokoro)"
      echo "                   Default: auto-detect from 'opencode --version' (falls back to v2)"
      echo "  --help           Show this help"
      exit 0
      ;;
    *) err "Unknown option: $arg"; exit 1 ;;
  esac
done

# Detect the installed OpenCode major version ("1", "2", or empty).
detect_opencode_major() {
  local ver
  if command -v opencode >/dev/null 2>&1; then
    ver="$(opencode --version 2>/dev/null | head -n1)"
    if [[ "$ver" =~ (^|[^0-9])([0-9]+)\. ]]; then
      echo "${BASH_REMATCH[2]}"
      return 0
    fi
  fi
  echo ""
}

# ---------------------------------------------------------------
# 1. System packages
# ---------------------------------------------------------------
if [[ "$SKIP_SYSTEM" -eq 0 ]]; then
  info "Installing system packages..."
  if [[ "$(id -u)" -ne 0 ]]; then
    warn "This step requires sudo. Running with sudo..."
    sudo apt-get update -qq
    sudo apt-get install -y ffmpeg pipewire-audio portaudio19-dev \
      python3.12-venv wtype xdotool socat espeak-ng
  else
    apt-get update -qq
    apt-get install -y ffmpeg pipewire-audio portaudio19-dev \
      python3.12-venv wtype xdotool socat espeak-ng
  fi

  # Add user to input group for /dev/input/event* access
  if ! id -nG "$USER" 2>/dev/null | grep -qw input; then
    info "Adding $USER to 'input' group (for keyboard access)..."
    sudo usermod -aG input "$USER"
    warn "You must log out and back in for group changes to take effect."
  fi
else
  info "Skipping system packages (--skip-system)"
fi

# ---------------------------------------------------------------
# 2. Install directory + Python venv
# ---------------------------------------------------------------
info "Setting up install directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy scripts
for script in voice.py tts_server.py speak.sh find_ptt_key.py \
              clean_for_speech.py grok_stop_speak.py; do
  cp "$REPO_DIR/scripts/$script" "$INSTALL_DIR/"
  info "Copied scripts/$script"
done
chmod +x "$INSTALL_DIR/speak.sh" "$INSTALL_DIR/find_ptt_key.py" \
  "$INSTALL_DIR/grok_stop_speak.py"

if [[ "$SKIP_VENV" -eq 0 ]]; then
  info "Creating Python venv..."
  if [[ ! -d "$INSTALL_DIR/.venv" ]]; then
    python3.12 -m venv "$INSTALL_DIR/.venv"
  fi
  source "$INSTALL_DIR/.venv/bin/activate"
  info "Installing Python dependencies..."
  pip install --quiet -r "$REPO_DIR/requirements.txt"
  info "Python environment ready."
else
  info "Skipping venv creation (--skip-venv)"
fi

# ---------------------------------------------------------------
# 3. OpenCode plugin
# ---------------------------------------------------------------
if [[ "$SKIP_PLUGIN" -eq 0 ]]; then
  # Overridable for testing (e.g. PLUGIN_DIR=/tmp/p install.sh --v1 ...).
  PLUGIN_DIR="${PLUGIN_DIR:-$HOME/.config/opencode/plugins}"
  mkdir -p "$PLUGIN_DIR"

  VARIANT="$PLUGIN_VARIANT"
  if [[ "$VARIANT" == "auto" ]]; then
    MAJOR="$(detect_opencode_major)"
    if [[ "$MAJOR" == "1" ]]; then
      VARIANT="v1"
    else
      VARIANT="v2"
      if [[ -z "$MAJOR" ]]; then
        warn "Could not detect OpenCode version; defaulting to the v2 plugin layout (use --v1 to force v1)."
      fi
    fi
  fi

  if [[ "$VARIANT" == "v1" ]]; then
    # V1 layout: single voice.ts + kokoro/clean.ts helper.
    # NOTE: the repo copy of plugin/kokoro/clean.ts is a re-export shim,
    # so install the canonical implementation (plugin/voice/clean.ts)
    # under the V1 path instead.
    mkdir -p "$PLUGIN_DIR/kokoro"
    cp "$REPO_DIR/plugin/voice/clean.ts" "$PLUGIN_DIR/kokoro/clean.ts"
    cp "$REPO_DIR/plugin/voice.ts" "$PLUGIN_DIR/voice.ts"
    info "OpenCode V1 plugin installed to $PLUGIN_DIR/voice.ts"
    # Remove any V2 install so the loaders don't see both layouts.
    if [[ -d "$PLUGIN_DIR/voice" ]]; then
      rm -rf "$PLUGIN_DIR/voice"
      info "Removed V2 plugin dir $PLUGIN_DIR/voice"
    fi
  else
    # V2 layout: voice/ is a plugin directory (server part: index.ts).
    # Helpers are co-located inside it so the loader treats the
    # directory as ONE plugin.
    mkdir -p "$PLUGIN_DIR/voice"
    for f in index.ts clean.ts speak.ts; do
      cp "$REPO_DIR/plugin/voice/$f" "$PLUGIN_DIR/voice/$f"
    done
    info "OpenCode V2 plugin installed to $PLUGIN_DIR/voice/index.ts (id: voice-kokoro)"
    # Remove the legacy V1 single-file install (V1 plugins do not run on v2
    # and a stale voice.ts would shadow/confuse the loader).
    if [[ -f "$PLUGIN_DIR/voice.ts" ]]; then
      rm -f "$PLUGIN_DIR/voice.ts"
      info "Removed legacy V1 plugin $PLUGIN_DIR/voice.ts"
    fi
    # Legacy helper dir from V1 installs is no longer needed by the V2
    # plugin (helpers live in voice/). Remove only our own file.
    if [[ -f "$PLUGIN_DIR/kokoro/clean.ts" ]]; then
      rm -f "$PLUGIN_DIR/kokoro/clean.ts"
      rmdir --ignore-fail-on-non-empty "$PLUGIN_DIR/kokoro" 2>/dev/null || true
      info "Removed legacy V1 helper $PLUGIN_DIR/kokoro/clean.ts"
    fi
  fi
else
  info "Skipping plugin (--skip-plugin)"
fi

# ---------------------------------------------------------------
# 3b. Grok Build Stop hook (TTS on turn end)
# ---------------------------------------------------------------
if [[ "$SKIP_GROK_HOOK" -eq 0 ]]; then
  GROK_HOOKS_DIR="$HOME/.grok/hooks"
  mkdir -p "$GROK_HOOKS_DIR"
  # Rewrite placeholder command to the installed absolute path.
  sed "s|__GROK_STOP_SPEAK__|$INSTALL_DIR/grok_stop_speak.py|g" \
    "$REPO_DIR/hooks/grok-voice.json" > "$GROK_HOOKS_DIR/grok-voice.json"
  info "Grok Build hook installed to $GROK_HOOKS_DIR/grok-voice.json"
  info "Restart grok or reload hooks (/hooks → r) for it to take effect."
else
  info "Skipping Grok hook (--skip-grok-hook)"
fi

# ---------------------------------------------------------------
# 4. Systemd services
# ---------------------------------------------------------------
if [[ "$SKIP_SERVICES" -eq 0 ]]; then
  SYSTEMD_DIR="$HOME/.config/systemd/user"
  mkdir -p "$SYSTEMD_DIR"
  cp "$REPO_DIR/systemd/opencode-voice.service" "$SYSTEMD_DIR/"
  cp "$REPO_DIR/systemd/opencode-tts.service" "$SYSTEMD_DIR/"
  systemctl --user daemon-reload
  systemctl --user enable opencode-voice.service opencode-tts.service
  info "Systemd services enabled (start on next login or run: systemctl --user start opencode-voice opencode-tts)"
else
  info "Skipping services (--skip-services)"
fi

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
echo ""
info "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Configure your PTT key:"
echo "     $INSTALL_DIR/.venv/bin/python $INSTALL_DIR/find_ptt_key.py"
echo "     Then edit $INSTALL_DIR/voice.py and set PTT_PATH + PTT_KEY"
echo ""
echo "  2. Log out and back in (for 'input' group + systemd services)"
echo ""
echo "  3. Test TTS:"
echo "     echo 'Hello world' | $INSTALL_DIR/speak.sh"
echo ""
echo "  4. Toggle voice output (OpenCode + Grok Build TTS):"
echo "     touch /tmp/opencode-voice-enabled   # enable"
echo "     rm -f /tmp/opencode-voice-enabled   # disable"
echo ""
echo "  5. Check service status:"
echo "     systemctl --user status opencode-voice opencode-tts"
echo ""
echo "  6. Grok Build: restart grok (or /hooks → r) so the Stop hook loads."
echo "     Built-in Grok STT (Ctrl+Space / F8) is separate from this stack."
echo ""
