#!/bin/bash
# Send stdin text to the Kokoro TTS daemon via Unix socket.
# Requires: socat
#
# Usage:
#   echo "Hello" | ./speak.sh

exec socat - UNIX-CONNECT:/tmp/opencode-tts.sock
