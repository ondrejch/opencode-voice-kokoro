import { Plugin } from "@opencode/plugin";
import { existsSync } from "node:fs";
import { cleanForSpeech } from "./clean.ts";
import {
  accumulatePartText,
  extractContextTexts,
  extractSessionID,
  selectSpokenText,
  speakText,
  DEFAULT_MAX_CHARS,
} from "./speak.ts";

// Voice on/off toggle: create or remove this file.
//   voice on:  touch /tmp/opencode-voice-enabled
//   voice off: rm -f /tmp/opencode-voice-enabled
const VOICE_FLAG = "/tmp/opencode-voice-enabled";

// Default path to the speak.sh wrapper (sends text to the Kokoro daemon).
// Overridable per install via plugin options: { "tts": "/path/to/speak.sh" }
function defaultTts(): string {
  return `${process.env.HOME ?? ""}/.local/share/opencode-voice/speak.sh`;
}

export default Plugin.define({
  id: "voice-kokoro",
  async setup(ctx) {
    const options = (ctx.options ?? {}) as Record<string, unknown>;
    const tts = typeof options["tts"] === "string" && options["tts"] ? (options["tts"] as string) : defaultTts();
    const flag = typeof options["flag"] === "string" && options["flag"] ? (options["flag"] as string) : VOICE_FLAG;
    const maxChars =
      typeof options["maxChars"] === "number" && options["maxChars"] > 0
        ? Math.floor(options["maxChars"] as number)
        : DEFAULT_MAX_CHARS;

    // Per-turn accumulator, keyed by streamed part index.
    const partTexts = new Map<number, string>();

    const controller = new AbortController();

    const onIdle = async (event: unknown): Promise<void> => {
      try {
        let accumulated = selectSpokenText(partTexts, maxChars);
        partTexts.clear();

        // Fallback when nothing streamed (e.g. plugin loaded mid-turn):
        // read the session transcript and speak the assistant text.
        if (!accumulated) {
          const sessionID = extractSessionID(event);
          if (sessionID && ctx.session && typeof ctx.session.context === "function") {
            try {
              const messages = await ctx.session.context({ sessionID } as never);
              accumulated = selectSpokenText(
                new Map([[0, extractContextTexts(messages as unknown)]]),
                maxChars,
              );
              if (accumulated === " ") accumulated = "";
            } catch {
              // Transcript unavailable; stay silent.
            }
          }
        }

        const text = cleanForSpeech(accumulated);

        // Voice output disabled.
        if (!existsSync(flag)) return;
        if (!text) return;

        await speakText(tts, text);
      } catch {
        // TTS must never break the agent loop.
      }
    };

    void (async () => {
      try {
        for await (const event of ctx.event.subscribe({ signal: controller.signal })) {
          const type = (event as { type?: unknown }).type;
          if (type === "message.part.updated") {
            accumulatePartText(partTexts, event);
          } else if (type === "session.idle") {
            await onIdle(event);
          }
        }
      } catch {
        // Subscription ended (unload) or stream errored; setup owns no retry.
      }
    })();

    console.log(`[voice-kokoro] loaded (tts=${tts})`);
    return () => controller.abort();
  },
});
