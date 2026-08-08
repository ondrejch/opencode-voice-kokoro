"""Tests for scripts/clean_for_speech.py — parity with tests/ts/test_clean_for_speech.ts."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "clean_for_speech.py"


def _load_clean():
    spec = importlib.util.spec_from_file_location("clean_for_speech", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["clean_for_speech"] = mod
    spec.loader.exec_module(mod)
    return mod.clean_for_speech


clean_for_speech = _load_clean()


class TestFencedCodeBlocks:
    def test_removes_triple_backtick(self):
        assert clean_for_speech("Here is code:\n```python\nx = 1\n```\nDone.") == (
            "Here is code: Done."
        )

    def test_removes_tilde_fenced(self):
        assert clean_for_speech("Code:\n~~~js\nconst y = 2;\n~~~\nEnd.") == "Code: End."

    def test_removes_multi_line_fenced(self):
        assert clean_for_speech("Start\n```\nline1\nline2\nline3\n```\nFinish") == (
            "Start Finish"
        )


class TestInlineCode:
    def test_preserves_inline_code_text(self):
        assert clean_for_speech("Use `large-v3` for STT") == "Use large-v3 for STT"

    def test_multiple_inline_spans(self):
        assert clean_for_speech("Set `foo` and `bar` then run") == (
            "Set foo and bar then run"
        )


class TestEmphasis:
    def test_bold(self):
        assert clean_for_speech("**Important:** tests passed") == (
            "Important: tests passed"
        )

    def test_strikethrough(self):
        assert clean_for_speech("~~old text~~ new text") == "old text new text"

    def test_italic_asterisk(self):
        assert clean_for_speech("This is *italic* text") == "This is italic text"

    def test_underscore_emphasis(self):
        assert clean_for_speech("file_test and _important_ value") == (
            "file_test and important value"
        )


class TestLinksAndUrls:
    def test_markdown_link(self):
        assert clean_for_speech("See [OpenCode](https://opencode.ai) docs") == (
            "See OpenCode docs"
        )

    def test_multiple_links(self):
        assert clean_for_speech("[a](http://a.com) and [b](http://b.com)") == "a and b"

    def test_bare_https(self):
        assert clean_for_speech("Visit https://example.com today") == "Visit today"

    def test_bare_http(self):
        assert clean_for_speech("Go to http://foo.bar/x?y=1 now") == "Go to now"


class TestPaths:
    def test_shortens_unix_path(self):
        assert clean_for_speech("Edit /home/user/project/src/voice.py please") == (
            "Edit voice.py please"
        )

    def test_shortens_deep_path(self):
        assert clean_for_speech(
            "Changed /home/o/git/111-AI/opencode-voice-kokoro/scripts/voice.py"
        ) == "Changed voice.py"


class TestStructure:
    def test_heading(self):
        assert clean_for_speech("### Installation") == "Installation"

    def test_heading_with_body(self):
        assert clean_for_speech("## Title\nSome content") == "Title Some content"

    def test_blockquote(self):
        assert clean_for_speech("> This is a quote") == "This is a quote"

    def test_unordered_list(self):
        assert clean_for_speech("- item one\n- item two") == "item one item two"

    def test_ordered_list(self):
        assert clean_for_speech("1. First\n2. Second") == "First Second"

    def test_asterisk_list(self):
        assert clean_for_speech("* item A\n* item B") == "item A item B"

    def test_horizontal_rule(self):
        assert clean_for_speech("Above\n---\nBelow") == "Above Below"


class TestWhitespaceAndEdges:
    def test_collapse_spaces(self):
        assert clean_for_speech("too    many     spaces") == "too many spaces"

    def test_collapse_newlines(self):
        assert clean_for_speech("line one\nline two\nline three") == (
            "line one line two line three"
        )

    def test_trim(self):
        assert clean_for_speech("  hello world  ") == "hello world"

    def test_empty(self):
        assert clean_for_speech("") == ""

    def test_whitespace_only(self):
        assert clean_for_speech("   \n\t  \n  ") == ""

    def test_plain_text(self):
        assert clean_for_speech("The tests passed successfully.") == (
            "The tests passed successfully."
        )


class TestRealistic:
    def test_realistic_agent_response(self):
        input_text = """I updated the server configuration.

```python
model = WhisperModel("large-v3", device="cuda")
```

The tests now pass. Changed **src/asr.py** and `src/config.py`.

See [docs](https://example.com/docs) for details.

### Summary
- Fixed the import
- Updated config at /home/user/project/config.yaml

> Note: restart the service."""

        result = clean_for_speech(input_text)
        assert "```" not in result
        assert "WhisperModel" not in result
        assert "**" not in result
        assert "`" not in result
        assert "https://" not in result
        assert "/home/" not in result
        assert "###" not in result
        assert "- Fixed" not in result
        assert "> Note" not in result
        assert "I updated the server configuration." in result
        assert "The tests now pass." in result
        assert "Fixed the import" in result
        assert "restart the service." in result
