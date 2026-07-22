---
name: branching
description: Git branching model, sync strategy, and commit conventions for this repo
triggers:
  - model
  - user
---

# Branching Model

## Hierarchy

```
main ← develop ← valedorsinho/epic/<name> ← valedorsinho/feature/<name>
         ↑
    hotfix/* (merges directly into main, bypasses develop)
```

- **Never commit to `main` or `develop`.**
- Feature branches merge only into their parent epic branch.
- **Hotfix branches (`hotfix/*`) merge directly into `main`**, not through `develop`. Use them for urgent production fixes only.

## Hotfix Workflow

```bash
# Branch off main
git checkout main
git checkout -b hotfix/<short-description>

# ... make fix, commit ...

# Merge directly into main
git checkout main
git merge hotfix/<short-description> --no-edit
git push origin main

# Clean up
git branch -d hotfix/<short-description>
git push origin --delete hotfix/<short-description>
```

## Sync Strategy

- **Epic ← develop**: `git merge origin/develop --no-edit` (never rebase epics)
- **Feature ← epic**: `git rebase origin/<epic>` + push with `--force-with-lease` 
- **Hotfix ← main**: branch off `main`, merge back into `main` directly

## Pre-edit Check

Before any edit, confirm you are on the right branch:

```bash
git branch --show-current
# If output is "main" or "develop" → STOP, do not proceed.
```

## Epic → Route Mapping

| Epic | Routes |
|---|---|
| `valedorsinho/epic/digital` | `checkout/`, `payload-suggested/`, `payload-validator/`, `ucp-agentic-commerce/` |
| `valedorsinho/epic/unified-commerce` | `terminal-payments/`, `terminal-fleet/`, `nfc-formatter/` |
| `valedorsinho/epic/tools-and-setup` | `setup/`, `management-api/`, `webhooks/` |
| `valedorsinho/epic/global-ui` | Theme toggle, layout, navigation, ApiCallCard |
| `valedorsinho/epic/code-refactor` | All refactor items |

## Commit Conventions

Format: `type(scope): description` using Conventional Commits.

Allowed types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `hotfix` 

## Commit Message Rules

- **No Devin attribution.** Do not include `Generated with [Devin]`, `Co-Authored-By: Devin`, or any AI-generated footer in commit messages.
- Keep messages concise: `type(scope): description` only. No body paragraphs unless truly necessary.

Examples:
```
feat(checkout): add stored card support to Drop-in
fix(api-layer): handle 401 refresh in apiFetch
refactor(global-ui): replace hardcoded hex colors with semantic Tailwind tokens
hotfix(docker): add .dockerignore to prevent macOS node_modules copy
```

---

## Verification

### Before every commit

```bash
# 1. Confirm not on a protected branch — must NOT output "main" or "develop"
git branch --show-current

# 2. Confirm working tree is clean or staged changes are intentional
git status

# 3. Preview the commit message before finalising
# Format: type(scope): description
# Allowed types: feat | fix | chore | docs | refactor | test | hotfix
```

### After committing

```bash
# 4. Confirm the commit message matches Conventional Commits format
git log --oneline -1
# Expected pattern: ^(feat|fix|chore|docs|refactor|test|hotfix)\([a-z-]+\): .+
```
If the most recent commit message does not match, amend it:
```bash
git commit --amend -m "type(scope): corrected message"
```

### After syncing an epic branch

```bash
# 5. Confirm merge (not rebase) was used — history should show a merge commit
git log --oneline --graph -5
# Expected: a "Merge branch" commit should appear, not a linear rebase history
```

### After syncing a feature branch

```bash
# 6. Confirm rebase was used — history should be linear (no merge commits)
git log --oneline --graph -5
# Expected: straight linear history, no merge commits
```
