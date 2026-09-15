---
name: deslop
description: Clean unnecessary code from a scoped diff while preserving behavior. Use before a commit or when asked to remove generated-code clutter.
---

# Clean the diff

Read [pstack-runtime](../pstack-runtime/SKILL.md).

Inspect the requested diff and surrounding conventions. Remove redundant wrappers, dead branches, duplicated checks, unused imports, speculative abstractions, and narration that the code already makes clear. Preserve meaningful validation, compatibility requirements, public API documentation and license headers. Do not expand into unrelated refactors. Run the relevant existing checks after behavioral edits; report the scope and evidence.
