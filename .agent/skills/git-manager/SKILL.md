# Skill: git-manager
**Description:** Worktree-aware Git handling for Dual-Agent (Dev/Tester) sync using OpenSpec and ENV-based authentication.

## Goal
To synchronize code changes between two parallel worktrees with zero friction, ensuring correct commit naming and automated pushes.

## Workflow

### 1. Identify Role & Environment
1. **Identify Role:**
   - If `pwd` contains `json2videoapi` (but NOT tester) -> Role: **Dev** (Branch: `main`)
   - If `pwd` contains `json2videoapi-tester` -> Role: **Tester** (Branch: `dev-testing`)

### 2. Sync State (The Handshake)
Before starting work, the agent must pull the latest data:
- `git fetch origin`
- **If Role is Dev:** `git merge origin/dev-testing` (Pull fixes from Tester)
- **If Role is Tester:** `git merge origin/main` (Pull features from Dev)
- **Check Status:** `git status`

### 3. Determine Commit Message
**Priority A: OpenSpec Proposal**
- Search `openspec/changes/*/proposal.md`.
- Read first line (e.g., `# Change: Improve Web Test`).
- **Formatting:**
    - If Role is **Tester**: `[TEST/FIX] <extracted_text>`
    - If Role is **Dev**: `feat: <extracted_text>`

**Priority B: Fallback**
- `[2026-01-24] Auto-commit: <brief_summary_of_changes>`

### 4. Stage and Commit
- `git add .`
- `git commit -m "<MESSAGE>"`

### 5. Push (Authentication Logic)
1. **Check Auth:** Check if `GITHUB_API_KEY` environment variable is set.
2. **If GITHUB_API_KEY is present:**
   - Get remote URL: `git remote get-url origin` (Example: `github.com/owner/repo`)
   - Execute: `git push https://$GITHUB_API_KEY@github.com/<owner>/<repo>.git`
3. **If GITHUB_API_KEY is NOT present:**
   - Execute: `git push`
4. **Missing Upstream Handling:** - If push fails with "no upstream", retry with:
     `git push --set-upstream origin $(git branch --show-current)`