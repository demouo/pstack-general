# Upstream provenance

Derived from [cursor/plugins pstack](https://github.com/cursor/plugins/tree/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack).

- Latest selectively synced revision: `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`
- Upstream plugin version: `0.15.9`
- Synced: 2026-10-05
- Original imported revision: `be432a96ed36e48d05f44bf375864355f62263f9` (2026-09-15)
- License: MIT, preserved in LICENSE with the original copyright notice.
- This is an independent portable adaptation, not an official harness integration.

The skill workflows, principle collection, playbooks, Benny operational instructions,
PR watcher and orchestration helpers derive from these revisions. Updates are selected
for portable behavior rather than copied wholesale. The portable runtime,
installer, generic setup/webhook instructions and worktree audit replace host-specific
integration. Upstream marketing guides, screenshots and plugin manifest are omitted.
The optional GitHub watcher retains recognition of existing review-bot comments,
including Cursor-authored review markers; this is data compatibility, not a runtime dependency.

The October update imports the new benchmark checklist, correction workflow and
measurement principle, plus relevant workflow and helper changes. It retains generic
verification safeguards and avoids vendor-specific model IDs, private transcript
paths and host-only scheduling commands. See the repository's
`docs/updates/2026-10-05.md` for the adaptation record (not installed in `.pstack/`).
