import type { Plugin } from "@opencode-ai/plugin"
import { existsSync } from "node:fs"
import { cleanForSpeech } from "./kokoro/clean.ts"

// Only the plugin itself may be exported from this module:
// OpenCode's legacy plugin loader invokes every function export as a plugin.

// Voice on/off toggle: create or remove this file.
//   voice on:  touch /tmp/opencode-voice-enabled
//   voice off: rm -f /tmp/opencode-voice-enabled
const VOICE_FLAG = "/tmp/opencode-voice-enabled"

// Path to the speak.sh wrapper (sends text to Kokoro daemon).
// Adjust if you install scripts elsewhere.
const TTS =
  `${process.env.HOME}/.local/share/opencode-voice/speak.sh`

export const VoicePlugin: Plugin = async ({
  client,
  $
}) => {

  const partTexts = new Map<number, string>()

  return {

    event: async ({ event }) => {

      // Accumulate text per part index as it streams.
      if (event.type === "message.part.updated") {

        const part = (event as any).properties?.part

        if (
          part?.type === "text" &&
          typeof part.text === "string"
        ) {
          partTexts.set(part.index, part.text)
        }
      }

      // When OpenCode finishes a turn, speak all text parts.
      if (event.type === "session.idle") {

        const accumulated = Array.from(partTexts.values()).join(" ")
        partTexts.clear()

        const text = cleanForSpeech(accumulated)

        // Voice output disabled
        if (!existsSync(VOICE_FLAG))
          return

        if (!text)
          return

        // Limit to last 800 characters to avoid very long speeches.
        const spoken =
          text.length > 800
            ? text.slice(-800)
            : text

        await $`echo ${spoken} | ${TTS}`
      }
    },
  }
}
