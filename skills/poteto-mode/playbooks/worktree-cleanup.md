### Worktree cleanup

1. Run the bundled `scripts/worktree-audit.sh [repo]`. It reads Git worktree metadata without fetching or deleting. It handles paths with spaces. Pass `--transcripts <workspace-export>` only when an explicitly scoped export is available.
2. Treat every clean worktree as requiring review. Unknown history does not prove inactivity. Check the branch, unpushed commits, PR status and active workers through the available tools. A closed PR alone does not prove its code was merged.
3. Preserve all tracked and untracked changes. Remove a worktree only when the user authorized cleanup and evidence establishes it is no longer needed. Use Git's worktree removal command without force; investigate refusal.
4. Run the audit again and report actual removed paths and remaining holds. Platform-specific simulator or cache cleanup is a separate, explicitly scoped operation.
