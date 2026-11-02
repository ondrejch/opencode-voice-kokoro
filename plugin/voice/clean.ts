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
