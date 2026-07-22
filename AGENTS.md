# Valedorsinho — AI Agent Context

FastAPI backend for [Adyen](https://www.adyen.com/) payment integration demos.
Hexagonal architecture. Deployed on Railway. Frontend lives in a separate repository.

**API Contract:** [`API_CONTRACT.md`](./API_CONTRACT.md)
Kept in sync with `docs/api-contracts/valedorsinho.md` in the frontend repo.

**Base URL:** `https://<valedorsinho-service>.up.railway.app`
In development, the Next.js frontend rewrites `/api/*` → `http://localhost:8000/api/*`.

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI + Uvicorn |
| Auth | Supabase (JWT — HS256 / RS256) |
| Database | Supabase (PostgreSQL, connection-pooled) |
| Payments SDK | Adyen Python library |
| Deployment | Railway |

---

## Repository Structure

```
app/
├── main.py                              # FastAPI app factory + lifespan
│
├── domain/                              # Core — no framework imports
│   ├── models/
│   │   ├── checkout.py                  # Amount, PaymentRequest, SessionsRequest, …
│   │   ├── terminal.py                  # DecodedTerminalResponse, PaymentSummaryField
│   │   ├── auth.py                      # UserRole, UserProfile, AdyenCredentials
│   │   └── webhook.py                   # WebhookEvent
│   └── verticals.py                     # Merchant vertical definitions
│
├── ports/                               # Abstract ABCs (driven-side interfaces)
│   ├── checkout_port.py
│   ├── terminal_port.py
│   ├── management_port.py
│   ├── validator_port.py
│   ├── auth_port.py
│   └── webhook_port.py
│
├── use_cases/                           # Orchestration services
│   ├── checkout_service.py
│   ├── terminal_payment_service.py
│   ├── terminal_fleet_service.py
│   ├── tools_service.py
│   ├── auth_service.py
│   └── webhook_service.py
│
├── adapters/                            # Concrete implementations (flat — no subfolders)
│   ├── checkout_adapter.py              # CheckoutGateway → Adyen
│   ├── management_adapter.py            # ManagementGateway → Adyen
│   ├── terminal_adapter.py              # TerminalGateway → Adyen
│   ├── terminal_decoder.py              # AdditionalResponse decoder
│   ├── validator_adapter.py             # PayloadValidator → OpenAPI spec
│   ├── supabase_adapter.py              # AuthGateway → Supabase
│   └── webhook_adapter.py              # WebhookGateway → Supabase
│
├── db/
│   └── migrations.py                    # Applies migrations/**.sql on startup
│
└── api/                                 # HTTP driving adapters
    ├── config.py                        # Env var constants (os.getenv only)
    ├── dependencies.py                  # FastAPI DI wiring (single source of truth)
    ├── routers/
    │   ├── checkout.py                  # /api/checkout/*
    │   ├── terminal_payments.py         # /api/terminal/*
    │   ├── terminal_fleet.py            # /api/fleet/*
    │   ├── tools.py                     # /api/tools/*
    │   ├── config.py                    # /api/config/*
    │   ├── auth.py                      # /api/auth/*
    │   └── webhooks.py                  # /api/webhooks/*
    └── schemas/
        ├── checkout.py, terminal.py, tools.py, auth.py, webhook.py

migrations/
└── *.sql                                # Numbered SQL files (001_, 002_, …) — auto-applied
```

---

## Connected Services

| Service | Purpose |
|---|---|
| Adyen | Checkout API (advanced + sessions), Terminal API (Nexo), Management API |
| Supabase | JWT verification, `adyen_configs` table, `profiles` table, `webhooks` table |
| Railway | Deployment host |

---

## Unique Facts

These are project-specific constraints not covered by any skill file.

### Amount Units

| Flow | Unit | Example |
|---|---|---|
| Online checkout (`/api/checkout/*`) | Minor units | `1000` = MXN 10.00 |
| Terminal payments (`/api/terminal/make-payment`) | Major units | `10.00` = MXN 10.00 |

### Webhook Routing

`POST /api/webhooks/{user_id}` — the `user_id` path parameter is the only routing key.
No Adyen payload parsing is needed to determine which user's inbox receives the event.

### Orphan Webhooks

If the `user_id` in the URL is not found in the `profiles` table, the webhook is still stored
with a default 3-day retention. This is intentional — do not reject unknown user IDs.

### Role Permissions

| Role | Config write | Webhook retention |
|---|---|---|
| `admin` | Yes | 5 days |
| `im` | Yes | 3 days |
| `user` | No | 3 days |

Roles are stored in the `profiles` Supabase table and resolved at runtime per request.

### Credential Lock

`adyen_configs.locked = true` prevents a user from overwriting their stored Adyen credentials.
Checked in `AuthService.upsert_adyen_config` before writing. (Known: check is not atomic — TOCTOU risk.)

### Demo Pages

This is a demo/integration backend — there are no end-user-facing pages served by FastAPI itself.
The frontend (separate repo) consumes the API. OpenAPI docs are at `/docs` (dev only).

---

## AI Contributor Rules

1. **Check current branch before any edit.** Run `git branch --show-current`. If output is `main` or `develop`, stop — do not proceed.
2. **No AI attribution footers in commit messages.** See the `branching` skill for the full commit convention and the explicit rule.
3. **Never push directly to `develop` or `main`.**
4. **Never stage or commit files inside `.devin/`.** The directory is gitignored by design and is per-machine config.
5. **Follow the `branching` skill** for all branch naming, sync strategy, commit format, and PR conventions.

---

## Skills Index

| Skill | Domain |
|---|---|
| `architecture` | Hexagonal layers, naming conventions, DI wiring, migration runner |
| `api-conventions` | Router patterns, Pydantic schema rules, error handling, typing conventions |
| `security` | Credential handling, JWT auth, webhook security, env vars, RLS |
| `branching` | Branching model, sync strategy, commit format, PR conventions |

---

## Workflows Index

| Workflow file | Trigger | Purpose |
|---|---|---|
| `update-context` | After a commit or structural change | Refresh the "Valedorsinho – Full Project Context" Supabase memory |
