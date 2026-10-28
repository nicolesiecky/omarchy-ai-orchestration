---
name: codex-query
description: >-
  Query OpenAI Codex CLI for code review, edge-case analysis, fuzzing, or alternative perspectives.
  Automatically falls back gracefully if Codex is offline or out of quota.
---

# Codex Query Skill

Use this skill when you need a fast second opinion, fuzzing edge cases, or structured validation from Codex.

## When to Use
- **Fuzzing & Edge Cases**: Asking for 10-15 edge-case payloads for a function.
- **Code Review**: Getting an alternative model's critique on a git diff or code snippet.
- **Schema Validation**: Validating or extracting complex JSON from unstructured text.

## Usage
Run the helper script directly:
```bash
~/.local/bin/codex-query "Your prompt here"
```

The script automatically queries Codex (`codex exec`) and falls back to Gemini Flash if Codex hits a quota or rate limit.
