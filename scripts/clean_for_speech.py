"""Markdown-aware text cleaning for TTS.

Mirrors plugin/voice.ts cleanForSpeech so OpenCode and Grok Build
produce the same spoken form from technical agent output.
"""

from __future__ import annotations

import re


def clean_for_speech(text: str) -> str:
    """Strip Markdown and paths so agent replies sound natural when spoken."""
    if not text:
        return ""

    # Remove fenced Markdown code blocks using ``` or ~~~.
    text = re.sub(r"```[\s\S]*?```|~~~[\s\S]*?~~~", " ", text)

    # Convert Markdown links to just their visible text.
    # [OpenCode](https://opencode.ai) -> OpenCode
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove standalone HTTP/HTTPS URLs.
    text = re.sub(r"https?:\/\/\S+", " ", text)

    # Shorten Unix filesystem paths to their final component.
    # /home/user/project/src/file.ts -> file.ts
    text = re.sub(r"(?:\/[\w.\-]+)+\/([\w.\-]+)", r"\1", text)

    # Remove inline-code backticks while preserving contents.
    # `large-v3` -> large-v3
    text = re.sub(r"`([^`\n]+)`", r"\1", text)

    # Remove Markdown bold markers.
    text = text.replace("**", "")

    # Remove Markdown strikethrough markers.
    text = text.replace("~~", "")

    # Remove Markdown italic markers (single * not surrounded by another *).
    text = re.sub(r"(?<!\*)\*(?!\*)", "", text)

    # Remove Markdown underscore emphasis.
    text = re.sub(r"(?<!\w)_(?=\S)|(?<=\S)_(?!\w)", "", text)

    # Remove Markdown heading markers.
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove Markdown blockquote markers.
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)

    # Remove unordered-list markers.
    text = re.sub(r"^\s*[-+*]\s+", "", text, flags=re.MULTILINE)

    # Remove ordered-list numbering.
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)

    # Remove Markdown horizontal rules.
    text = re.sub(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$", " ", text, flags=re.MULTILINE)

    # Collapse all whitespace to single spaces and trim.
    text = re.sub(r"\s+", " ", text).strip()

    return text
