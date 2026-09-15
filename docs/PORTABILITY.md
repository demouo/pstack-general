# Portability contract and migration notes

## Layers

1. `skills/` holds the portable workflow instructions. Every entry reads `pstack-runtime` before execution. Read sibling skills explicitly when native discovery is absent.
2. `pstack-runtime` maps workflow roles to actual session capabilities. It is an instruction contract, not an executable provider SDK or a new agent runtime.
3. The installer copies a self-contained bundle to `.pstack/` and optionally adds a managed instruction block to a user-selected file. It never assumes that a harness supports native skill discovery at that location.
4. Shell/Node/Bun helpers remain optional and run through the available shell. Connector and scheduler implementations belong to the host or user's configured provider.

## Removed assumptions

| Upstream dependency | Portable behavior |
| --- | --- |
| Plugin manifest and project plugin settings | Plain file bundle with explicit instruction entrypoint |
| Private model slugs and effort encoded in slugs | Inherited model or validated host-supported override |
| Task-specific subagent types, cloud flags, background flags | Role prompts with actual delegation schema and host limits |
| Mandatory parallel or cross-family review | Sequential fallback with reduced independence disclosed; independent shipping gates stay unmet |
| Always-applied model rule | Runtime-read `.pstack/models.md` or user config |
| Derived private transcript paths and fixed JSONL schema | Workspace history API or explicit scoped export; current-conversation fallback |
| Built-in authoring and team cleanup plugins | Bundled `author-skill` and `deslop` |
| Loop, goal, cloud sleeper and restart guarantees | Real scheduler when available; durable checkpoint and manual resume otherwise |
| Provider-specific webhook/secret cards | Documented provider contract, server-side secrets, local mock until configured |
| Editor-only automation creation | Available scheduler interface; tested event binding required |
| Private application cache cleanup | Scoped Git worktree audit and explicit cleanup |

Slash names remaining in examples mean workflow names, not required host commands. Control skill names mean a suitable project or host capability; pstack-runtime supplies the fallback. Connector-specific source playbooks describe optional integrations and must inspect actual schemas before calling them.

The GitHub watcher still recognizes review-bot metadata from upstream, including Cursor bot markers, without calling Cursor services. GraphQL pagination cursors are unrelated to the editor. Graphite-backed frontier computation is an explicit optional tool dependency and has not been replaced by an inaccurate generic stack guess.

## Install and refresh

`python3 scripts/install.py --target <project> [--entrypoint <filename>] [--dry-run]`

The install manifest records hashes of managed files. Unchanged managed files can update; modified managed files cause a conflict before writes. Removed source-managed files can be removed only when their installed hash still matches the manifest. User-only files remain. Inspect and merge a conflict manually; there is no force-overwrite switch. Installation does not commit, push, activate automations or change the host's global settings. The installer preflights conflicts but does not promise crash-atomic updates across the entire directory.

To stop automatic loading, remove the marked pstack block from the chosen instruction file. Before removing `.pstack/`, preserve any user configuration or state stored inside it. No uninstall command deletes user state automatically.

## Validation scope

Tests cover repeat installation, entrypoint preservation, local-edit conflict handling, dry-run, symlink/path rejection, worktree paths with spaces, untracked-file preservation, skill identities and real relative reference targets. The upstream Bun suite exercises orchestration state and PR watcher policy with fixtures. These tests do not establish that a particular hosted session grants delegation, scheduler, secrets or app-control access.

Manual acceptance in any target harness:

1. Load `how` by explicit installed path and answer a small repository question with file evidence.
2. Run `interrogate` without delegation and confirm it reports same-agent passes without claiming multi-model consensus.
3. Run `recall` without history access and confirm it uses only current context or an explicitly supplied export.
4. Request a long-running workflow without a scheduler and confirm it saves a handoff rather than claiming a future wake.
5. Prepare Benny without a provider and confirm it stays dormant with unresolved integration requirements.

The local pi run now exercises related file/native loading, review, TDD, history and scheduler scenarios. See [the pi validation report](validation/pi-2026-09-15.md) for real results and limits. Other target environments and the Benny integration scenario remain unverified.
