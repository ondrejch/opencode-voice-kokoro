import type { Plugin } from "@opencode-ai/plugin"
import { existsSync } from "node:fs"

// Voice on/off toggle: create or remove this file.
//   voice on:  touch /tmp/opencode-voice-enabled
//   voice off: rm -f /tmp/opencode-voice-enabled
const VOICE_FLAG = "/tmp/opencode-voice-enabled"

// Path to the speak.sh wrapper (sends text to Kokoro daemon).
// Adjust if you install scripts elsewhere.
const TTS =
  `${process.env.HOME}/.local/share/opencode-voice/speak.sh`

export function cleanForSpeech(text: string): string {
  return text
    // Remove fenced Markdown code blocks using ``` or ~~~.
    .replace(/```[\s\S]*?```|~~~[\s\S]*?~~~/g, " ")

    // Convert Markdown links to just their visible text.
    // [OpenCode](https://opencode.ai) -> OpenCode
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")

    // Remove standalone HTTP/HTTPS URLs.
    .replace(/https?:\/\/\S+/g, " ")

    // Shorten Unix filesystem paths to their final component.
    // /home/user/project/src/file.ts -> file.ts
    .replace(/(?:\/[\w.\-]+)+\/([\w.\-]+)/g, "$1")

    // Remove inline-code backticks while preserving contents.
    // `large-v3` -> large-v3
    .replace(/`([^`\n]+)`/g, "$1")

    // Remove Markdown bold markers.
    // **important** -> important
    .replace(/\*\*/g, "")

    // Remove Markdown strikethrough markers.
    // ~~old~~ -> old
    .replace(/~~/g, "")

    // Remove Markdown italic markers (single * not surrounded by another *).
    .replace(/(?<!\*)\*(?!\*)/g, "")

    // Remove Markdown underscore emphasis.
    .replace(/(?<!\w)_(?=\S)|(?<=\S)_(?!\w)/g, "")

    // Remove Markdown heading markers.
    // ### Title -> Title
    .replace(/^\s{0,3}#{1,6}\s+/gm, "")

    // Remove Markdown blockquote markers.
    // > quote -> quote
    .replace(/^\s*>\s?/gm, "")

    // Remove unordered-list markers.
    // - item -> item
    .replace(/^\s*[-+*]\s+/gm, "")

    // Remove ordered-list numbering.
    // 1. item -> item
    .replace(/^\s*\d+[.)]\s+/gm, "")

    // Remove Markdown horizontal rules.
    .replace(/^\s*(?:-{3,}|\*{3,}|_{3,})\s*$/gm, " ")

    // Collapse all whitespace to single spaces.
    .replace(/\s+/g, " ")

    // Trim leading/trailing whitespace.
    .trim();
}

export const VoicePlugin: Plugin = async ({
  client,
  $
}) => {

  let accumulated = ""

  return {

    event: async ({ event }) => {

      // Accumulate the full assistant text as it streams.
      if (event.type === "message.part.updated") {

        const part = (event as any).properties?.part

        if (
          part?.type === "text" &&
          typeof part.text === "string"
        ) {
          accumulated = part.text
        }
      }

      // When OpenCode finishes a turn, speak the cleaned text.
      if (event.type === "session.idle") {

        const text = cleanForSpeech(accumulated)
        accumulated = ""

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
