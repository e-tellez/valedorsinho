# 🤝 Contributing to Valedorsinho

This document defines the collaboration standards for this repository. Every contributor — human or AI — must follow these rules consistently.

---

## 🌿 Branching Model

This repo uses the same **Scrum-based, project-namespaced branching model** as the frontend workspace.

### Base Branches

| Branch    | Purpose                                      | Accepts PRs from             |
|-----------|----------------------------------------------|------------------------------|
| `main`    | Production-ready. Always deployable.         | `develop` only               |
| `develop` | Primary integration branch.                  | `valedorsinho/epic/*` only   |

> ⚠️ **Never push directly to `main` or `develop`.**

### Work Branches

```
develop
└── valedorsinho/epic/<description>        ← Scrum epic. Branched from develop.
    └── valedorsinho/feature/<description>  ← Scrum task. Branched from its parent epic.
```

**Rules:**
- Feature branches only merge back into their parent epic — **never directly into `develop`**.
- Epic branches merge into `develop` via PR when the epic is complete.

**Examples:**
```
valedorsinho/epic/digital
valedorsinho/epic/unified-commerce
valedorsinho/feature/checkout-sessions-endpoint
valedorsinho/feature/webhook-hmac-validation
```

### Full Workflow

```
develop → valedorsinho/epic/<name> → valedorsinho/feature/<name>
       ← PR into epic               ← PR epic into develop    ← PR develop into main
```

---

## 🔀 Merge & Rebase Strategy

| Branch type                              | Sync with           | Strategy                              | Push                 |
|------------------------------------------|---------------------|---------------------------------------|----------------------|
| `develop` / `main`                       | —                   | No rebase. Merge only.                | Regular push         |
| `valedorsinho/epic/*`                    | `origin/develop`    | `git merge origin/develop --no-edit`  | Regular push         |
| `valedorsinho/feature/*` (unmerged)      | parent epic         | `git rebase origin/<parent-epic>`     | `--force-with-lease` |

> ⚠️ **Never rebase shared or epic branches.** Rebasing rewrites commit hashes, causing diverged history and "Can't automatically merge" errors on PRs.

### Syncing an Epic Branch with Develop

```bash
git fetch origin
git merge origin/develop --no-edit
git push origin valedorsinho/epic/<name>
```

---

## ✍️ Commit Convention — Conventional Commits

Format: `type(scope): description`

| Type       | When to use                                 |
|------------|---------------------------------------------|
| `feat`     | New feature                                 |
| `fix`      | Bug fix                                     |
| `refactor` | Code restructure without behavior change    |
| `chore`    | Build, config, dependencies                 |
| `docs`     | Documentation only                          |
| `test`     | Adding or updating tests                    |
| `hotfix`   | Critical prod fix branched from `main`      |

**Examples:**
```
feat(checkout): add sessions flow endpoint
fix(webhooks): correct expires_at calculation for admin role
refactor(auth): extract token verification to supabase_adapter
chore(deps): bump fastapi to 0.115
docs(api): update webhook contract for /adyen/{user_id}
```

---

## 📬 Pull Requests

### Naming
```
[Epic] Brief description of what was done
```

Examples:
- `[Digital] Add Sessions checkout flow`
- `[Tools & Setup] Implement webhook ingest and retention`
- `[Supabase Auth] Add role-based config write access`

### Body Template

```markdown
## What was done
- Bullet list of changes

## Why it was done
The problem or Scrum task this solves.

## How to test
curl/Postman commands to verify, or steps to reproduce.
```

---

## 📁 Project Structure Conventions

- All source code lives under `app/`
- **Hexagonal architecture layers (inner → outer):** `domain/` → `ports/` → `use_cases/` → `adapters/` → `api/`
- No framework imports inside `domain/` or `ports/`
- All adapters are flat — no subfolders inside `adapters/`
- Database migrations live in `migrations/*.sql` and are auto-applied on startup via `db/migrations.py`
- API contract is maintained in `API_CONTRACT.md` and kept in sync with the frontend's `docs/api-contracts/valedorsinho.md`

---

## 🤖 AI Contributor Rules

When an AI (e.g. Windsurf Cascade) contributes to this repo, it must:
1. Identify the correct epic before writing code
2. Confirm it is on the correct `valedorsinho/feature/<name>` branch
3. Follow all branching, commit, and PR conventions above
4. Never push directly to `develop` or `main`
