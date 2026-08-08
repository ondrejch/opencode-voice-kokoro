import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { cleanForSpeech } from "../../plugin/voice.ts";

describe("cleanForSpeech", () => {

  // --- Fenced code blocks ---

  it("removes triple-backtick fenced code blocks", () => {
    const input = "Here is code:\n```python\nx = 1\n```\nDone.";
    assert.equal(cleanForSpeech(input), "Here is code: Done.");
  });

  it("removes tilde fenced code blocks", () => {
    const input = "Code:\n~~~js\nconst y = 2;\n~~~\nEnd.";
    assert.equal(cleanForSpeech(input), "Code: End.");
  });

  it("removes multi-line fenced code blocks", () => {
    const input = "Start\n```\nline1\nline2\nline3\n```\nFinish";
    assert.equal(cleanForSpeech(input), "Start Finish");
  });

  // --- Inline code ---

  it("preserves inline code text but removes backticks", () => {
    assert.equal(cleanForSpeech("Use `large-v3` for STT"), "Use large-v3 for STT");
  });

  it("handles multiple inline code spans", () => {
    assert.equal(
      cleanForSpeech("Set `foo` and `bar` then run"),
      "Set foo and bar then run",
    );
  });

  // --- Bold / italic / strikethrough ---

  it("removes bold markers preserving text", () => {
    assert.equal(cleanForSpeech("**Important:** tests passed"), "Important: tests passed");
  });

  it("removes strikethrough markers preserving text", () => {
    assert.equal(cleanForSpeech("~~old text~~ new text"), "old text new text");
  });

  it("removes single-asterisk italic markers", () => {
    assert.equal(cleanForSpeech("This is *italic* text"), "This is italic text");
  });

  it("removes underscore emphasis", () => {
    assert.equal(cleanForSpeech("file_test and _important_ value"), "file_test and important value");
  });

  // --- Links ---

  it("converts markdown links to visible text only", () => {
    assert.equal(
      cleanForSpeech("See [OpenCode](https://opencode.ai) docs"),
      "See OpenCode docs",
    );
  });

  it("handles multiple links in one string", () => {
    assert.equal(
      cleanForSpeech("[a](http://a.com) and [b](http://b.com)"),
      "a and b",
    );
  });

  // --- URLs ---

  it("removes bare HTTP URLs", () => {
    assert.equal(
      cleanForSpeech("Visit https://example.com today"),
      "Visit today",
    );
  });

  it("removes bare HTTPS URLs", () => {
    assert.equal(
      cleanForSpeech("Go to http://foo.bar/x?y=1 now"),
      "Go to now",
    );
  });

  // --- Paths ---

  it("shortens Unix paths to final component", () => {
    assert.equal(
      cleanForSpeech("Edit /home/user/project/src/voice.py please"),
      "Edit voice.py please",
    );
  });

  it("shortens deep paths to final directory or file", () => {
    assert.equal(
      cleanForSpeech("Changed /home/o/git/111-AI/opencode-voice-kokoro/scripts/voice.py"),
      "Changed voice.py",
    );
  });

  // --- Headings ---

  it("removes heading markers", () => {
    assert.equal(cleanForSpeech("### Installation"), "Installation");
  });

  it("removes atx heading with text after", () => {
    assert.equal(
      cleanForSpeech("## Title\nSome content"),
      "Title Some content",
    );
  });

  // --- Blockquotes ---

  it("removes blockquote markers", () => {
    assert.equal(cleanForSpeech("> This is a quote"), "This is a quote");
  });

  // --- Lists ---

  it("removes unordered list markers", () => {
    assert.equal(cleanForSpeech("- item one\n- item two"), "item one item two");
  });

  it("removes ordered list numbering", () => {
    assert.equal(cleanForSpeech("1. First\n2. Second"), "First Second");
  });

  it("removes asterisk list markers", () => {
    assert.equal(cleanForSpeech("* item A\n* item B"), "item A item B");
  });

  // --- Horizontal rules ---

  it("removes horizontal rules", () => {
    assert.equal(cleanForSpeech("Above\n---\nBelow"), "Above Below");
  });

  // --- Whitespace ---

  it("collapses multiple spaces into one", () => {
    assert.equal(cleanForSpeech("too    many     spaces"), "too many spaces");
  });

  it("collapses newlines into spaces", () => {
    assert.equal(cleanForSpeech("line one\nline two\nline three"), "line one line two line three");
  });

  it("trims leading and trailing whitespace", () => {
    assert.equal(cleanForSpeech("  hello world  "), "hello world");
  });

  // --- Edge cases ---

  it("handles empty string", () => {
    assert.equal(cleanForSpeech(""), "");
  });

  it("handles whitespace-only string", () => {
    assert.equal(cleanForSpeech("   \n\t  \n  "), "");
  });

  it("handles plain text with no markdown", () => {
    assert.equal(cleanForSpeech("The tests passed successfully."), "The tests passed successfully.");
  });

  // --- Combined real-world OpenCode output ---

  it("cleans a realistic OpenCode response", () => {
    const input = `I updated the server configuration.

\`\`\`python
model = WhisperModel("large-v3", device="cuda")
\`\`\`

The tests now pass. Changed **src/asr.py** and \`src/config.py\`.

See [docs](https://example.com/docs) for details.

### Summary
- Fixed the import
- Updated config at /home/user/project/config.yaml

> Note: restart the service.`;

    const result = cleanForSpeech(input);
    // Should not contain code blocks, backticks, bold markers, URLs, paths, headings, list markers, or blockquote markers
    assert.ok(!result.includes("```"));
    assert.ok(!result.includes("WhisperModel"));
    assert.ok(!result.includes("**"));
    assert.ok(!result.includes("`"));
    assert.ok(!result.includes("https://"));
    assert.ok(!result.includes("/home/"));
    assert.ok(!result.includes("###"));
    assert.ok(!result.includes("- Fixed"));
    assert.ok(!result.includes("> Note"));
    // Should contain the natural-language sentences
    assert.ok(result.includes("I updated the server configuration."));
    assert.ok(result.includes("The tests now pass."));
    assert.ok(result.includes("Fixed the import"));
    assert.ok(result.includes("restart the service."));
  });
});
