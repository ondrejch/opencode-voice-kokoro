import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, readFileSync, existsSync, chmodSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { cleanForSpeech } from "../../plugin/voice/clean.ts";
import { cleanForSpeech as cleanLegacy } from "../../plugin/kokoro/clean.ts";
import {
  accumulatePartText,
  extractContextTexts,
  extractPartText,
  extractSessionID,
  selectSpokenText,
  speakText,
} from "../../plugin/voice/speak.ts";
import plugin from "../../plugin/voice/index.ts";

describe("voice plugin clean parity", () => {
  it("re-export matches canonical implementation", () => {
    const samples = [
      "Hello **world**",
      "See [docs](https://example.com/x) at /home/u/p/file.ts",
      "```py\nx = 1\n```\nDone",
      "> quote\n- item\n1. first\n### Title",
    ];
    for (const s of samples) assert.equal(cleanLegacy(s), cleanForSpeech(s));
  });
});

describe("extractPartText", () => {
  it("reads V1 shape event.properties.part", () => {
    const event = { type: "message.part.updated", properties: { part: { type: "text", text: "hi", index: 2 } } };
    assert.deepEqual(extractPartText(event), { index: 2, text: "hi" });
  });

  it("reads bare event.part shape", () => {
    assert.deepEqual(extractPartText({ part: { type: "text", text: "yo" } }), { index: 0, text: "yo" });
  });

  it("ignores non-text parts", () => {
    assert.equal(extractPartText({ properties: { part: { type: "image", index: 0 } } }), undefined);
  });

  it("ignores user-role parts", () => {
    const event = { properties: { part: { type: "text", text: "q", role: "user" } } };
    assert.equal(extractPartText(event), undefined);
  });

  it("ignores empty text", () => {
    assert.equal(extractPartText({ part: { type: "text", text: "" } }), undefined);
  });
});

describe("accumulatePartText + selectSpokenText", () => {
  it("orders by part index and caps length at the tail", () => {
    const store = new Map<number, string>();
    accumulatePartText(store, { properties: { part: { type: "text", text: "second", index: 1 } } });
    accumulatePartText(store, { properties: { part: { type: "text", text: "first", index: 0 } } });
    // Later update to the same index wins (streaming re-send).
    accumulatePartText(store, { properties: { part: { type: "text", text: "FIRST", index: 0 } } });
    assert.equal(selectSpokenText(store), "FIRST second");
    assert.equal(selectSpokenText(store, 6), "second");
    assert.equal(selectSpokenText(new Map()), "");
  });
});

describe("extractSessionID", () => {
  it("finds session ids in several shapes", () => {
    assert.equal(extractSessionID({ sessionID: "abc" }), "abc");
    assert.equal(extractSessionID({ properties: { sessionID: "def" } }), "def");
    assert.equal(extractSessionID({ type: "session.idle" }), undefined);
  });
});

describe("extractContextTexts", () => {
  it("joins assistant text parts, skips users and non-text", () => {
    const messages = [
      { info: { role: "user" }, parts: [{ type: "text", text: "question" }] },
      { info: { role: "assistant" }, parts: [{ type: "text", text: "answer one" }, { type: "tool", text: "x" }] },
      { info: { role: "assistant" }, parts: [{ type: "text", text: "answer two" }] },
    ];
    assert.equal(extractContextTexts(messages), "answer one answer two");
    assert.equal(extractContextTexts({ messages }), "answer one answer two");
    assert.equal(extractContextTexts([]), "");
  });
});

describe("speakText", () => {
  it("pipes text to the tts script stdin without a shell", async () => {
    const dir = mkdtempSync(join(tmpdir(), "voice-tts-"));
    const out = join(dir, "out.txt");
    const script = join(dir, "tts.sh");
    writeFileSync(script, `#!/bin/sh\ncat >> ${out}\n`);
    chmodSync(script, 0o755);
    await speakText(script, "hello tts");
    assert.equal(readFileSync(out, "utf8"), "hello tts");
  });

  it("resolves (never throws) when the script is missing", async () => {
    await speakText("/nonexistent/speak.sh", "hi");
  });
});

function mockCtx(events: unknown[], options: Record<string, unknown>, contextResult: unknown = []) {
  return {
    options,
    event: {
      subscribe: (_opts: unknown) => ({
        async *[Symbol.asyncIterator]() {
          for (const e of events) yield e;
        },
      }),
    },
    session: {
      context: async () => contextResult,
    },
  };
}

describe("voice-kokoro plugin setup (v2 entrypoint)", () => {
  it("has id voice-kokoro and a setup function", () => {
    assert.equal(plugin.id, "voice-kokoro");
    assert.equal(typeof plugin.setup, "function");
  });

  it("speaks streamed parts on session.idle when the flag exists", async () => {
    const dir = mkdtempSync(join(tmpdir(), "voice-e2e-"));
    const out = join(dir, "out.txt");
    const script = join(dir, "tts.sh");
    writeFileSync(script, `#!/bin/sh\ncat >> ${out}\n`);
    chmodSync(script, 0o755);
    const flag = join(dir, "enabled");
    writeFileSync(flag, "");

    const ctx = mockCtx(
      [
        { type: "message.part.updated", properties: { part: { type: "text", text: "Hello **there**", index: 0 } } },
        { type: "session.idle", properties: { sessionID: "s1" } },
      ],
      { tts: script, flag },
    );
    const cleanup = await plugin.setup(ctx as never);
    // Let the background subscription drain.
    for (let i = 0; i < 100 && !existsSync(out); i++) await new Promise((r) => setTimeout(r, 20));
    assert.equal(readFileSync(out, "utf8"), "Hello there");
    assert.equal(typeof cleanup, "function");
    (cleanup as () => void)();
  });

  it("stays silent when the flag file is absent", async () => {
    const dir = mkdtempSync(join(tmpdir(), "voice-off-"));
    const out = join(dir, "out.txt");
    const script = join(dir, "tts.sh");
    writeFileSync(script, `#!/bin/sh\ncat >> ${out}\n`);
    chmodSync(script, 0o755);

    const ctx = mockCtx(
      [
        { type: "message.part.updated", properties: { part: { type: "text", text: "Hi", index: 0 } } },
        { type: "session.idle", properties: {} },
      ],
      { tts: script, flag: join(dir, "missing-flag") },
    );
    const cleanup = await plugin.setup(ctx as never);
    await new Promise((r) => setTimeout(r, 200));
    assert.equal(existsSync(out), false);
    (cleanup as () => void)();
  });

  it("falls back to session.context when nothing streamed", async () => {
    const dir = mkdtempSync(join(tmpdir(), "voice-fb-"));
    const out = join(dir, "out.txt");
    const script = join(dir, "tts.sh");
    writeFileSync(script, `#!/bin/sh\ncat >> ${out}\n`);
    chmodSync(script, 0o755);
    const flag = join(dir, "enabled");
    writeFileSync(flag, "");

    const ctx = mockCtx([{ type: "session.idle", properties: { sessionID: "s9" } }], { tts: script, flag }, [
      { info: { role: "assistant" }, parts: [{ type: "text", text: "Fallback **answer**" }] },
    ]);
    const cleanup = await plugin.setup(ctx as never);
    for (let i = 0; i < 100 && !existsSync(out); i++) await new Promise((r) => setTimeout(r, 20));
    assert.equal(readFileSync(out, "utf8"), "Fallback answer");
    (cleanup as () => void)();
  });
});
