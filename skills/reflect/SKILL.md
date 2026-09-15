---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.
---

Read [pstack-runtime](../pstack-runtime/SKILL.md) before executing this workflow. It defines capability checks, model defaults, and fallback behavior.


# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

## When to invoke

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## Process

### 1. Locate the active transcript

The parent finds its own transcript file before fanning out. Use only the active workspace history exposed by the harness or an explicitly configured transcript directory. If unavailable, use the current conversation and report the history gap. Do not glob across `unrelated workspaces`. That crosses workspace boundaries and reads private chats from unrelated projects.

Inspect the actual history format and match by conversation identity and content. Do not assume a provider-specific JSONL schema. If no history resolves, write a digest of the current session and pass that instead.

### 2. Spawn three reviewers in parallel

One message, three delegation calls, a general-purpose role prompt, explicit `model:` on each, read-only permissions including connector reads. Reviewers need MCP access for context lookups (tickets, chat threads, observability traces referenced in the transcript). Use the host permission model; do not grant write access just to read connectors.

| Lens | `model` | Prompt template |
|---|---|---|
| Judgment | your configured reflect-judgment model (default `inherit-parent`) | `references/judgment-reviewer.md` |
| Tooling | your configured reflect-tooling model (default `inherit-parent`) | `references/tooling-reviewer.md` |
| Divergent | your configured reflect-judgment model (default `inherit-parent`) | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in the delegation response body.

### 3. Synthesize

One delegation call, a general-purpose role prompt, using your configured reflect-judgment model (default `inherit-parent`), read-only permissions including connector reads. The synthesizer's quality check includes spot-verifying citations, which can require MCP access. Use the host permission model; do not grant write access just to read connectors. Use `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. The synthesizer returns a structured Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the synthesizer's Accepted list. For any item that would be enforced more reliably by a lint rule, script, metadata flag, or runtime check, move it from Accepted to Backlog. See the **encode-lessons-in-structure** principle skill.

### 5. Apply

Before applying any Accepted edit, present the synthesizer's full Accepted/Rejected/Backlog output to the user and wait for explicit approval. The user picks which subset to apply and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

Backlog items file to whatever devex / backlog tracker your team uses automatically. Only the Accepted list waits for approval.

For each approved Accepted item, follow the Routing field exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): parent does directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): hand to the bundled **author-skill** skill and run its draft / test / iterate loop.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): hand to `author-skill` and run its description-optimization loop.
- `new skill via author-skill: <kebab-name>`: hand creation to `author-skill`. Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done. Skip this step if it doesn't.

### 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
