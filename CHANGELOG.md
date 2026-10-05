# Changelog

## v0.3.0 — 2026-10-05

- Install skills directly into project `.agents/skills/<skill-name>/` for native discovery.
- Keep pstack configuration, state, provenance and optional automations under `.pstack/`.
- Migrate v1 manifests and unchanged managed skills without overwriting local edits or unrelated skills.
- Refresh existing marked instruction blocks; preserve unmanaged legacy files and user configuration.
- Update both READMEs, runtime paths, Benny setup and pi validation helpers.

## v0.2.0 — 2026-10-05

Selectively sync upstream pstack 0.15.9 at `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`.

- Add `benchmark-checklist`, `correct` and `principle-explain-the-number` (53 skills total).
- Strengthen architectural guardrails, schema-backed TypeScript casts and performance investigation.
- Preserve decision logs with append-only corrections and run boundaries; initialize empty logs safely.
- Require verification identities and measurement methods, fresh scoped worker rounds and explicit stuck-child accounting.
- Update PR descriptions, draft readiness, code-ready verification, rebase timing and conservative build-result reuse.
- Bind hourly audit suggestions to actual scheduler capabilities; keep unchanged ticks quiet.
- Allow configured verifier models in the plan checker and add helper regression tests and pi smoke fixtures.

## v0.1.0 — 2026-09-15

Initial portable adaptation of upstream `be432a96ed36e48d05f44bf375864355f62263f9`: runtime capability contract, 50 skills, project installer, optional local helpers and real pi validation.
