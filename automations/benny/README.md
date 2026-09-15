# Benny

Portable Slack issue triage and reproduction workflow templates. Requires a configured Slack event runner, tracker, repository access and app-control adapter. No jobs run merely by installing this pack.

Point your agent at [FOR_AGENTS.md](FOR_AGENTS.md), with the target repository and desired integrations. Setup validates configuration, prepares provider-specific job specifications and tests thread safety before enabling authorized jobs. Keep secret values in your runner's secret store.
