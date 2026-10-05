# pi validation: `.agents/skills/` layout

Date: 2026-10-05. Local pi: 0.84.1, started with Node 26. No global harness configuration was changed.

## Native discovery

The installer placed 53 skill folders in a fresh project's `.agents/skills/` without creating an instruction entrypoint. `validate_pi_discovery.mjs` ran the installed pi's real default resource loader, with no additional skill paths or `--skill` equivalent:

```json
{
  "expected": 53,
  "discovered": 53,
  "missing": [],
  "diagnostics": []
}
```

The test used an empty temporary pi agent directory, in-memory settings and project trust for the known fixture. It disabled extensions, prompt templates and themes. It made no model request and wrote no user trust settings. This verifies discovery by this local pi version; other harnesses still need their actual discovery behavior checked.

Reproduce with a fresh installed project:

```sh
python3 scripts/install.py --target /tmp/pstack-discovery-project
node scripts/validate_pi_discovery.mjs /path/to/installed/pi/dist /tmp/pstack-discovery-project
```

The helper targets pi's resource-loader API used by version 0.84.1; it requires a local pi installation. On this machine the distribution is `/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/dist`, and the Node binary is `/opt/homebrew/opt/node/bin/node`.

## Real model sessions

Two isolated pi sessions using the existing `deepseek/deepseek-v4.1-flash-expires-on-0910` model completed with exit code 0, an `agent_end` event and no model errors:

| Case | Evidence |
| --- | --- |
| `how` by installed file path | Read `.agents/skills/how/SKILL.md`, runtime and references; explained the pricing module with source citations. This was a static explanation, with no claim of independent verification. |
| `interrogate` with native skill parsing | Loaded `.agents/skills/` through pi's `--skill` option, read the installed runtime, reproduced the pricing defects and disclosed same-agent review limitations. |

The main process confirmed both sessions read `pstack-runtime` and left source/test fixtures unchanged. These sessions verify execution after relocation; the separate default resource-loader test establishes discovery without explicit paths. Raw local session evidence remains in `/tmp/pstack-pi-agents-layout-20261005/`.

Reproduce the live sessions with a new output directory:

```sh
python3 scripts/validate_pi.py \
  --output /tmp/pstack-layout-live-another-run \
  --node /opt/homebrew/opt/node/bin/node \
  --case how --case interrogate
```

## Installer verification

- 17 Python tests cover fresh installation, repeated updates, local edits, other skills, legacy migration, dry-run, path/symlink rejection, retired files and instruction preservation.
- Migration from the actual published v0.2.0 archive succeeded: skills moved to `.agents/skills/`, the marked entrypoint updated, and model policy, run state and an unrelated skill remained intact.
- Relative links in installed skills and automation files resolved, and 53 skill schemas validated.
- Historical reports remain unchanged because they describe the installation layout tested at that time.
