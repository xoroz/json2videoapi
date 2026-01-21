name: git-manager 
description: Simple git handling. Checks status, adds changes, and commits using OpenSpec proposal titles or a timestamped fallback.

# Git Manager Skill

## Goal
To save code changes to git with minimal friction, prioritizing OpenSpec naming conventions for commit messages and handling authentication via environment variables if provided.

## Workflow

### 1. Check Status
Always run this command first to verify the current state of the repo:
```bash
git status
```

### 2. Determine Commit Message
The agent must determine the commit message based on the following logic:

#### Priority A: OpenSpec Proposal
- **Search**: Look for any file matching the pattern `openspec/changes/*/proposal.md`.
- **Read**: If found, read the first line of that file.
- **Parse**: Expect a format like `# Change: Improve Web Test`.
- **Set Message**: Extract the text following `# Change: ` to use as the commit message (e.g., "Improve Web Test").

#### Priority B: Fallback
- **Condition**: If no `proposal.md` is found or the header is missing.
- **Set Message**: Create a message with the current timestamp and a brief, AI-generated summary of what changed.
- **Format**: `[YYYY-MM-DD HH:MM] Auto-commit: <brief_summary_of_changes>`

### 3. Stage and Commit
Once the message is determined, execute these commands in order:

**Stage all changes**:
```bash
git add .
```

**Commit**:
```bash
git commit -m "<MESSAGE>"
```

### 4. Push
Push the changes to the remote, handling authentication and upstream issues.

**Authentication Check**:
Before pushing, check if the `GITHUB_API_KEY` environment variable is set.

**If `GITHUB_API_KEY` is present**:
Construct the push URL with the token and execute:
```bash
# (Agent must replace <owner>/<repo> with actual values from 'git remote get-url origin')
git push https://$GITHUB_API_KEY@github.com/<owner>/<repo>.git
```

**If `GITHUB_API_KEY` is NOT present**:
Simply run:
```bash
git push
```

**Missing Upstream Handling**:
If the push fails due to a missing upstream branch (regardless of authentication method), retry with:
```bash
git push --set-upstream origin <current_branch>
```
