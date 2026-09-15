---
name: setup-benny
description: Configure Benny issue triage and reproduction workflows with a scheduler, Slack connector, tracker, and app-control adapter.
---

# Set up Benny

Read the installed pstack-runtime skill. Benny is a dormant automation pack; copying it does not register jobs or authorize messages. Do not create or update jobs until the user asks. Never commit secrets.

## 1. Install the pack and shared skills

Install the portable pstack bundle in the target repository using `scripts/install.py --target <repository>`. It includes this pack at `.pstack/automations/benny/` and shared skills at `.pstack/skills/`. Confirm that the scheduler's checkout can read both directories and its configured instruction entrypoint. If updating, inspect conflicts and preserve local changes.

Verify access to `how`, `why`, `tdd`, `unslop`, and the principle skills by explicit file path; native slash-skill discovery is optional. Keep user-owned configuration and maps outside the pack, for example `.pstack/benny/`. A remote runner needs the secret-free pack and configuration committed on its checkout branch before it can read them. Do not commit without authorization.

## 2. Adapt the configuration

Open these copied examples:

- `../../templates/configuration.example.yaml`
- `../reproduce-and-fix-issues/references/feature-map.example.md`

Create user-owned copies outside `.pstack/automations/benny/`. These are configuration files, not pack files. Example locations:

- Project config, such as `.pstack/benny/configuration.yaml`
- Project feature map, such as `.pstack/benny/feature-map.md`
- Project routing map, such as `.pstack/benny/routing.md`
- User config, such as `~/.config/benny/configuration.yaml`
- User feature map, such as `~/.config/benny/feature-map.md`

Fill one feature-map section for every user-facing feature the automation may reproduce. Keep it at the user point of view. Do not freeze implementation details or current code paths in the map.

Do not edit the copied examples. Pack refreshes may update source-managed files after conflict review, but they must never touch the user-owned copies.

Prefer committed, secret-free files in the target repository when a fresh automation checkout must read them. Otherwise paraphrase the required values into the live prompt. Verify referenced files exist in the branch checked out by the runner.

Use stable repository-relative paths for committed pack and configuration files. Never reference the plugin source directory or a plugin cache path from a live automation.

## 3. Fill the required choices

Ask for or confirm:

- Source Slack channel ID
- Optional operations or status channel ID
- Repository URL and default branch
- Triage identity or Slack user ID
- Issue tracker type, team, project, labels, and intake status
- Tracker adapter skill or MCP actions
- Optional routing map path
- Required control skill name
- Required user-facing feature-map path
- Status emoji strings
- Pull request URL format
- Polling and effort budgets
- Model slug for triage, repro, code work, and media review

Use only model slugs shown as available in the harness's advertised model list or supported model list. Do not guess a slug and do not carry over a private default.

The source channel, triage identity, repository, tracker adapter, control skill, and feature map must be explicit. Fail setup if any required value stays ambiguous.

Use pstack's `unslop` skill on the final automation names, descriptions, and prompt shims before saving them.

## 4. Check integration capabilities

The triage automation needs:

- Read access to the configured source Slack channel and its threads
- Thread-reply access in that channel
- Attachment metadata and file download access when reports include media
- Search, read, create, and update access through the configured issue-tracker adapter

The repro automation needs:

- Read access to the source thread
- Thread-reply access in the source channel
- Optional post and edit access in the configured operations channel
- Repository read and history access
- A pull request action that can open a draft pull request
- The configured control-adapter skill

Prefer configured Slack connector actions for reads and posts. The optional `BENNY_SLACK_BOT_TOKEN` may fill a narrow gap such as editing one operations status message or downloading an attachment. Store the value in a secret manager or environment, not in YAML.

Do not use undocumented integration endpoints.

## 5. Prepare the routing map

If the user wants reroutes or owner pings:

1. Copy `../triage-issue-reports/references/routing.example.md` outside `.pstack/automations/benny/`.
2. Replace every placeholder with public or organization-local values.
3. Keep owner pings off by default.
4. Allow a ping only for a configured feature owner or a confirmed likely regression author.

If no routing map is configured, triage may classify a report but must not guess a destination or owner.

## 6. Verify the control adapter

Read `../reproduce-and-fix-issues/references/control-adapter.md` and the user's completed feature map.

Confirm that the named skill can:

- Bring up the target app
- Navigate every mapped feature through the real UI
- Exercise mapped states through declared adapter actions
- Inspect state without forcing the result
- Capture screenshots
- Start and stop a recording
- Clean up its processes and temporary data

If any capability is missing, leave the repro automation disabled. It must fail closed rather than claim a reproduction it did not perform.

## 7. Prepare the live automations

Read `../../FOR_AGENTS.md` and both templates under `../../templates/`. Bind their trigger and payload to the documented scheduler or event runner available in this environment. Verify its Slack event envelope, source coordinates, bot identity, repository checkout, secrets and concurrency behavior. A generic timer is not automatically a Slack event trigger.

For each workflow, prepare a job specification with its name, trigger, source channel, repository/ref, exact operational skill path, configuration path, permissions, budgets, and expected output. Triage follows `.pstack/automations/benny/skills/triage-issue-reports/SKILL.md`; reproduction follows `.pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md`. Each job must also read `.pstack/skills/pstack-runtime/SKILL.md`.

Use the provider's supported create/update API or UI after user authorization. Inspect existing jobs before creating duplicates. Honor provider-required review steps. If no scheduler/event integration exists, leave the specifications as drafts and report that automated execution is unavailable. Do not invent endpoints or claim a running job.

Keep jobs disabled for normal traffic until the test below passes in a test channel or runner. If disabled jobs cannot run tests, use the provider's isolated test mechanism and verify production permissions separately before enabling.

## 8. Test thread safety

Use a test channel or a harmless test report.

Before testing, confirm that the portable `.pstack/skills/`, `.pstack/automations/benny/`, and every referenced secret-free configuration file are committed on the branch used by the automation checkout. Confirm that both live prompts point at their exact committed operational files. If any check fails, stop. Tell the user that the automation cannot be enabled yet.

Verify:

1. Triage stores the root `thread_ts` and posts exactly one verdict as a reply.
2. The verdict contains one configured marker.
3. Repro accepts the marker only from the configured triage identity.
4. Repro keeps the same immutable source coordinates.
5. No source-channel root message appears.
6. A delegated worker cannot use any Slack write action.
7. Missing coordinates, a deleted parent, or a failed preflight produces no post and no tracker issue.

Enable normal traffic only after all seven checks pass.
