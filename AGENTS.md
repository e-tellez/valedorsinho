# Project Rules for AI Agents

## Commit Conventions

Format: `type(scope): description` — Conventional Commits only.

Allowed types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `hotfix`

- **No AI attribution.** Never include `Generated with [Devin]`, `Co-Authored-By: Devin`, or any AI-generated footer in commit messages.
- Keep the message to one line (`type(scope): description`). No body paragraphs unless truly necessary.

```
feat(checkout): add stored card support to Drop-in
fix(api-layer): handle 401 refresh in apiFetch
chore(gitignore): exclude .devin/ from tracking
```

## Branch Protection

- **Never commit directly to `main` or `develop`.**
- **Before committing or pushing**, always confirm:
  1. Current branch: `git branch --show-current`
  2. That the branch name matches the changes being made — e.g. do not commit repo-infrastructure changes on a feature branch scoped to a specific product change.
  3. If the branch doesn't match, ask the user which branch to use before proceeding.

## .devin/ Policy

- `.devin/` is always local-only. Never stage or commit files inside it.
- If `git status` shows a `.devin/` file staged, unstage immediately: `git restore --staged .devin/`

## Available Skills

Invoke these when working in the relevant domain:

| Skill | When to invoke |
|---|---|
| `branching` | Branching, merging, sync strategy |
| `architecture` | Hexagonal layers, DI wiring, adding new features |
| `api-conventions` | Routers, schemas, error handling, typing |
| `security` | Credentials, JWT, webhooks, Adyen integration |
