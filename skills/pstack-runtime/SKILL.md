---
name: pstack-runtime
description: Resolve pstack capabilities, model policy, paths, and fallbacks before running a pstack workflow in any agent harness.
---

# Portable runtime contract

This contract governs the execution assumptions in all bundled workflows and role prompts. Follow the host's instructions and the user's scope and authorization. Workflow prose does not grant new permissions. Slash names are shorthand: read the sibling `<name>/SKILL.md` when native skill invocation is unavailable.

## Discover only what the task needs

Use the tools actually exposed in the current session. A harness name alone does not prove a capability exists. Do not invent tool names, parameters, model IDs, private endpoints, filesystem stores, or background persistence.

| Capability | Preferred binding | Fallback |
| --- | --- | --- |
| Read/edit/search/run | Host tools or shell | Ask for the necessary artifact if filesystem access is absent |
| Delegation | Available spawn/send/wait/status tools with their documented schema | Perform the roles sequentially in this session |
| Model selection | Explicit, supported per-role choice | Omit overrides and inherit the current model |
| History | Workspace-scoped history API or user-configured export | Current conversation and persisted handoff; disclose missing history |
| Connectors | Exposed MCP, connector, or documented authenticated CLI | Local evidence; name inaccessible sources |
| App control | Available browser, terminal, simulator, or project verification scripts | Report blocked live verification; static checks are not live proof |
| Scheduling | User-authorized native scheduler or existing external runner | Bounded in-session execution, then write a resumable handoff |
| Secrets | Host secret store or server environment | Document required secret names; never request secret values in chat |

Use a plain checklist if there is no todo tool; a plain question if there is no structured question tool. Use text or Mermaid when image generation is unavailable. An unavailable optional helper must not stop unrelated work.

## Roles and models

Read project `.pstack/models.md`, or `~/.config/pstack/models.md` when the project file is absent. Explicit user/session settings take precedence. Missing configuration means `inherit-parent` for all roles. `auto` also means omit the model override, never a literal provider model ID. A model and reasoning effort are separate host-specific options; never synthesize IDs by appending an effort suffix.

Panel workflows default to four candidate/reviewer passes. Repeated `inherit-parent` entries mean four passes, not four model families. Respect the host's concurrency and nesting limits. If delegation is unavailable or disallowed, execute those passes sequentially, save separate outputs, and disclose that they are same-agent passes with reduced independence. Never call them independent or multi-model verification. Repetition by the same agent is not corroboration: do not count passes as independent votes or raise confidence because they agree. If a shipping step requires an independent verdict, leave that gate unmet until a separate authorized reviewer supplies it.

Role names describe prompts, not registered agent types. Read [poteto-agent](references/agents/poteto-agent.md) for playbook workers and [comment-sicko](references/agents/comment-sicko.md) for comment cleanup, and pass the relevant instructions to an available worker or apply them locally. Do not recursively delegate when already executing that role. Keep review-only roles read-only even when connector access exists.

## Paths and lifecycle

Resolve bundled files relative to the skill being read, never the shell working directory. Invoke scripts by their resolved absolute path. New project skills default to `.agents/skills/`; if the host cannot discover that directory, load them by explicit file path or use the user's configured skills root. No global plugin installation is required.

Use project `.pstack/state/<run>/` for durable plans, checkpoints and orchestration state. Supply this path explicitly to helper scripts. Keep secrets and private transcripts out of version control. Only read transcript roots explicitly supplied for this workspace; do not derive paths from workspace slugs or scan other projects. Exports may be Markdown, text or JSONL: inspect the actual format rather than assuming a schema.

A cloud worker is optional placement. Choose local or remote execution based on available tools, repository access and required runtime. Never assume children share files, inherit a worktree, survive a restart, or support nesting. Give each writer an isolated worktree or disjoint ownership. After restart, check live status before resuming or replacing workers. A scheduler must actually be registered before claiming future work will happen.

## External actions and proof

Only send messages, create scheduled jobs, push, publish, merge or deploy within explicit user authorization and host policy. Broad workflow defaults cannot authorize unrelated actions. Use drafts when readiness is unproven. Do not reset dirty worktrees to recover; preserve changes and use a clean isolated checkout.

Report what ran, what was observed, and which required capabilities were missing. Never upgrade missing history, unavailable connectors, same-agent review, or static checks into stronger evidence.
