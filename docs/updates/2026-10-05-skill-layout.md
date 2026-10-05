# v0.3.0: Shared skill directory

Skills now install directly into `.agents/skills/<skill-name>/`. This follows the [Agent Skills discovery recommendation](https://github.com/agentskills/agentskills/blob/main/docs/client-implementation/adding-skills-support.mdx). The format specification does not mandate an installation path. [pi supports this directory](https://pi.dev/docs/latest/skills); unsupported hosts can use the installed file paths or an instruction entrypoint.

## Layout

```text
project/
├── .agents/skills/
│   ├── how/SKILL.md
│   ├── poteto-mode/SKILL.md
│   ├── pstack-runtime/SKILL.md
│   └── ...
└── .pstack/
    ├── install-manifest.json
    ├── LICENSE
    ├── UPSTREAM.md
    ├── automations/benny/
    ├── models.md          # optional user model policy
    └── state/             # created by workflows when needed
```

Skill folders retain their scripts, references and assets. Sibling skill links keep working. Benny remains an optional automation pack, rather than an automatically invoked general skill.

## Install or migrate

```sh
python3 scripts/install.py --target /absolute/path/to/project
```

Add `--entrypoint AGENTS.md`, `CLAUDE.md`, `GEMINI.md` or the actual instruction filename when needed. No entrypoint is created by default.

Existing v0.1.0/v0.2.0 installations refresh in place:

1. Validate the old inventory, destination paths and all conflicts before writing.
2. Copy skills to `.agents/skills/`, update support files and write the v2 manifest.
3. Remove retired managed files only when their content matches the old inventory. Empty retired directories can be removed; unmanaged files stay where they are.
4. Refresh existing marked blocks in regular `AGENTS.md`, `CLAUDE.md` and `GEMINI.md`. Pass the original `--entrypoint` for another filename.

User model policy, run state, unrelated skills and unmanaged files remain. Edited legacy skills or conflicting destination files stop migration; inspect and merge before retrying. `--dry-run` creates no files. Updates preflight conflicts but are not crash-atomic across both directories.

Historical pi reports describe their original installation layout and remain unchanged. Current validation scripts use `.agents/skills/`.

## Verification

17 Python tests pass. Migration from the published v0.2.0 archive preserved user state, model policy and an unrelated skill; installed relative links resolved. The local pi 0.84.1 default resource loader discovered all 53 skills without explicit skill paths, and two real model sessions completed against the relocated skills. See the [layout validation report](../validation/pi-agents-layout-2026-10-05.md) for evidence and reproduction.
