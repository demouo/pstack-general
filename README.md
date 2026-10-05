# pstack · Portable harness edition

**English** | [简体中文](README.zh-CN.md)

A plain Markdown skill bundle adapted from [Cursor pstack](https://github.com/cursor/plugins/tree/main/pstack) for coding agent runtimes (harnesses). It covers code exploration, design review, implementation, verification, PR monitoring, long-task recovery and engineering principles, with portable replacements for Cursor plugin installation, private paths, model IDs and tool parameters.

**Minimum requirement: your harness can read files and follow instructions.** Running code requires a shell. Delegation, multiple models, browsers, history and scheduling depend on the capabilities available in the current session. Without delegation, roles can run sequentially; reviews by the same agent do not count as independent reviews.

## Quick start

### One-sentence installation

Copy this sentence into your harness:

```text
Get the latest pstack from https://github.com/demouo/pstack-general, follow its README to install the skills into this project's .agents/skills/ and connect them to this harness, preserve existing skills, instructions and user configuration, and verify that the skills can be loaded.
```

### Manual installation

The installer requires only Python 3.9+. Clone this repository or extract a Release archive, then run:

```sh
python3 scripts/install.py --target /absolute/path/to/project
```

Skills install directly into `.agents/skills/<skill-name>/`, the shared discovery location recommended by [Agent Skills](https://github.com/agentskills/agentskills/blob/main/docs/client-implementation/adding-skills-support.mdx). Each folder contains `SKILL.md` and its supporting resources. Harnesses that support this location can discover them natively; [pi](https://pi.dev/docs/latest/skills) supports it. Other harnesses can use explicit paths or an instruction entrypoint.

`.pstack/` holds only pstack support files: the install manifest, license, provenance and optional automation pack. User model policy and run state also stay there. Existing skills and user configuration are preserved; a conflicting local edit or unrelated same-name skill file stops the update before writing. Rerun to update, or use `--dry-run` to preview.

For instruction-based loading, optionally choose the file your harness actually reads:

```sh
# For environments that read AGENTS.md
python3 scripts/install.py --target /absolute/path/to/project --entrypoint AGENTS.md

# For environments that read CLAUDE.md
python3 scripts/install.py --target /absolute/path/to/project --entrypoint CLAUDE.md

# For environments that read GEMINI.md
python3 scripts/install.py --target /absolute/path/to/project --entrypoint GEMINI.md

```

In Codex, Claude Code, Gemini CLI, OpenCode, Cursor or another harness, the most portable way to invoke a skill is by its installed file path:

> Read `.agents/skills/how/SKILL.md` and follow its workflow to explain this repository's authentication module.

> Read `.agents/skills/poteto-mode/SKILL.md` and use the full pstack workflow to implement this feature.

Native discovery, slash commands and runtime capabilities vary by harness. If automatic loading is unavailable, name the paths above in your session. Installation does not change global configuration or register background tasks.

### Upgrade an older installation

Rerun the installer in the same target project. It migrates unchanged managed skills from `.pstack/skills/` to `.agents/skills/`, and refreshes existing marked pstack blocks in `AGENTS.md`, `CLAUDE.md` and `GEMINI.md`. For another entrypoint filename, pass `--entrypoint` with that filename. Local edits or destination conflicts stop the migration before writes. Unmanaged legacy files, model policy and run state remain in place. See the [layout migration notes](docs/updates/2026-10-05-skill-layout.md).

## Common workflows

| Task | Skill |
| --- | --- |
| Full engineering workflow and playbook routing | `poteto-mode` |
| Understand an implementation / trace design decisions | `how` / `why` |
| Compare alternatives / design architecture | `arena` / `architect` |
| Adversarial review / parallel coverage | `interrogate` / `swarm` |
| Test-driven development / impact analysis | `tdd` / `blast-radius` |
| Vet performance measurements / explain measured numbers | `benchmark-checklist` / `principle-explain-the-number` |
| Prevent recurring agent mistakes | `correct` |
| Technical writing / remove redundancy | `technical-writing` / `unslop` / `deslop` |
| Reflect / recover context / record decisions | `reflect` / `recall` / `show-me-your-work` |
| Create or maintain real application verification workflows | `create-verification-skill` / `maintain-verification-skill` |
| Configure model policy | `setup-pstack` |
| Triage and reproduce Slack reports | `automations/benny/FOR_AGENTS.md` |

Browse all 53 skills in the [skill directory](skills/). Put optional model policy in the target project's `.pstack/models.md`; missing configuration inherits the current session's model. Skills read this policy without changing the host's model settings.

The current portable release, `v0.3.0`, uses `.agents/skills/` for installation and selectively syncs upstream pstack `0.15.9` (2026-10-05). It includes performance evidence checks and recurring mistake prevention, plus architecture, logging, verification and autonomous workflows with capability fallbacks. See the [upstream update record](docs/updates/2026-10-05.md) for the adaptation choices.

## Optional tool dependencies

- `worktree-audit.sh`: Python 3.9+ and Git; reads local state without needing chat history.
- `check-plan.mjs`: Node.js; checks multi-PR plan formatting.
- `scripts/orch/orch.ts`: Bun; pass `--store` explicitly. `frontier set` also requires Graphite `gt` stack metadata; other state operations do not. It manages state, rather than starting or waking agents.
- `scripts/watch-pr/watch-pr`: Bun, GitHub CLI `gh` and repository permissions. Supports GitHub only.
- Bun tools install dependencies from the lockfile on first use. They are optional for reading skills.
- Benny and the webhook UI require a user-selected event runner, connectors and secret configuration. Without those bindings, they produce drafts rather than running integrations.

## Validation

```sh
python3 -m unittest discover -s tests -v
cd skills/poteto-mode/scripts
bun install --frozen-lockfile
bun test orch watch-pr
bun run typecheck
```

See [PORTABILITY.md](docs/PORTABILITY.md) for migration details, and [UPSTREAM.md](UPSTREAM.md) and [LICENSE](LICENSE) for source provenance and the MIT license. Real local pi 0.84.1 sessions verified five initial scenarios: file/native skill loading, review fallback, a TDD fix, missing history and missing scheduling. See the [initial pi report](docs/validation/pi-2026-09-15.md). Two additional scenarios cover benchmark vetting and recurring mistake prevention; see the [October pi report](docs/validation/pi-2026-10-05.md). The [layout validation report](docs/validation/pi-agents-layout-2026-10-05.md) verifies discovery of all 53 skills in `.agents/skills/`, two live sessions and migration from v0.2.0. The upstream update record and earlier pi reports are in Chinese. Other harnesses have not each been tested end to end.
