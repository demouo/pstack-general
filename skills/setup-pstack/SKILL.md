---
name: setup-pstack
description: Configure pstack role models and capability choices for the current harness. Use for setup-pstack, model budgets, or changes to pstack execution settings.
---

# Setup pstack

Read [pstack-runtime](../pstack-runtime/SKILL.md).

1. Inspect available tools and any existing project `.pstack/models.md` (or user `~/.config/pstack/models.md`). Preserve user choices.
2. Default every role to `inherit-parent`. Model selection is optional. When the user wants a specific model, verify that the host exposes it; never guess a model ID or rewrite it to encode reasoning effort.
3. Write the selected scope's `models.md` as a plain Markdown table with columns `Role`, `Model`, and `Reasoning effort`. Effort defaults to `inherit`; only use advertised values. Panel model values are comma-separated lists, one pass per entry.
4. Roles: `feature, refactoring`, `bug-fix`, `perf-issue`, `hillclimb`, `judgment and prose`, `hardest tasks`, `how explorer`, `how explainer`, `why investigators`, `why synthesizer`, `reflect tooling`, `reflect judgment, divergent, synthesizer`, `arena runners`, `arena cross-judge pool`, `swarm workers`, `architect runners`, `interrogate reviewers`. Missing roles inherit the current model; panels default to four passes.
5. Confirm the saved file and summarize available delegation, history, app control and scheduling. This is runtime-read configuration, not an automatically applied host rule. Do not claim that it changes the host's model picker.
6. If the project lacks a real-app verification recipe, mention the bundled `create-verification-skill` workflow when relevant.
