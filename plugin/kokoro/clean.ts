// Canonical implementation moved to ../voice/clean.ts for the OpenCode v2
// plugin layout (plugin/voice/ is a single plugin directory).
// This module stays as a compatibility re-export for the legacy V1
// plugin (plugin/voice.ts) and existing tests.
export { cleanForSpeech } from "../voice/clean.ts";
