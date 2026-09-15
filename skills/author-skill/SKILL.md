---
name: author-skill
description: Write or update a portable SKILL.md and its supporting references for a repeatable agent workflow.
---

# Author a skill

Read [pstack-runtime](../pstack-runtime/SKILL.md).

Inspect the existing skill and its callers first. Preserve scope and user intent. Use a lowercase hyphenated folder name and matching YAML `name`, plus a concise `description` describing when to use it. Quote punctuation-sensitive values. Keep entry instructions short and link substantial references relative to the skill. Include scripts only for repeatable deterministic work.

Use capabilities rather than host tool names. Describe fallback behavior for optional capabilities and required evidence when a capability is missing. Do not grant permissions through a skill. Preserve explicit-only invocation preferences using the host's supported metadata if available; do not assume frontmatter flags are universal.

Check frontmatter, referenced paths, and scripts. For a material workflow change, walk a realistic request through the instructions and check its outputs. Report whether this was a real execution or an instruction review. Avoid adding rules without a demonstrated need.
