# 🛒 Valedorsinho — Backend

FastAPI backend for [Adyen](https://www.adyen.com/) payment integration demos. Built with **hexagonal architecture** and deployed on Render. The frontend lives in a separate repository.

**API Contract:** [`API_CONTRACT.md`](./API_CONTRACT.md)

See [CONTRIBUTING.md](./CONTRIBUTING.md) for branching, commit, and PR standards.

---

## 🗺️ Feature Roadmap

### 1. Digital
| Feature | Endpoints | Status |
|---------|-----------|--------|
| **Checkout — Advanced Flow** | `POST /api/checkout/payments`, `POST /api/checkout/payments/details` | ✅ |
| **Checkout — Sessions Flow** | `POST /api/checkout/sessions` | ✅ |
| **Tokenisation** | `CardOnFile` via Advanced flow | ✅ |
| **Payload Validator** | `POST /api/tools/validate` | ✅ |
| **Vertical Suggestions** | `GET /api/tools/suggested/{vertical}` | ✅ |

### 2. Unified Commerce
| Feature | Endpoints | Status |
|---------|-----------|--------|
| **Terminal Payments** | `POST /api/terminal/payment` | ✅ |
| **Terminal Fleet Management** | `GET /api/fleet/*` | ✅ |

### 3. Tools & Setup
| Feature | Endpoints | Status |
|---------|-----------|--------|
| **Config** | `GET /api/config/client`, `GET /api/config/environment` | ✅ |
| **Auth** | `GET /api/auth/config`, `POST /api/auth/config` | ✅ |
| **Webhooks** | `POST /api/webhooks/adyen/{user_id}`, `GET /api/webhooks`, `GET /api/webhooks/{id}` | ✅ |

---

## 🏗️ Architecture — Hexagonal

```text
app/
├── main.py                              # FastAPI app factory + lifespan
│
├── domain/                              # CORE — no framework dependencies
│   ├── models/
│   │   ├── checkout.py                  # Amount, PaymentRequest, SessionsRequest, etc.
│   │   ├── terminal.py                  # DecodedTerminalResponse, PaymentSummaryField
│   │   ├── auth.py                      # UserRole, UserProfile, AdyenCredentials
│   │   └── webhook.py                   # WebhookEvent
│   └── verticals.py                     # Merchant vertical definitions
│
├── ports/                               # PORTS — abstract interfaces (driven side)
│   ├── checkout_port.py                 # CheckoutGateway ABC
│   ├── terminal_port.py                 # TerminalGateway ABC
│   ├── management_port.py               # ManagementGateway ABC
│   ├── validator_port.py                # PayloadValidator ABC
│   ├── auth_port.py                     # AuthGateway ABC
│   └── webhook_port.py                  # WebhookGateway ABC
│
├── use_cases/                           # USE CASES — orchestration
│   ├── checkout_service.py
│   ├── terminal_payment_service.py
│   ├── terminal_fleet_service.py
│   ├── tools_service.py
│   ├── auth_service.py
│   └── webhook_service.py
│
├── adapters/                            # ADAPTERS — driven side (external)
│   ├── checkout_adapter.py              # CheckoutGateway → Adyen
│   ├── management_adapter.py            # ManagementGateway → Adyen
│   ├── terminal_adapter.py              # TerminalGateway → Adyen
│   ├── validator_adapter.py             # PayloadValidator → OpenAPI spec
│   ├── terminal_decoder.py              # AdditionalResponse decoder
│   ├── supabase_adapter.py              # AuthGateway → Supabase
│   └── webhook_adapter.py              # WebhookGateway → Supabase
│
├── db/
│   └── migrations.py                    # Auto-applies pending SQL migrations on startup
│
└── api/                                 # DRIVING ADAPTERS — HTTP layer
    ├── config.py                        # Env var constants
    ├── dependencies.py                  # FastAPI DI wiring
    ├── routers/
    │   ├── checkout.py                  # /api/checkout/*
    │   ├── terminal_payments.py         # /api/terminal/*
    │   ├── terminal_fleet.py            # /api/fleet/*
    │   ├── tools.py                     # /api/tools/*
    │   ├── config.py                    # /api/config/*
    │   ├── auth.py                      # /api/auth/*
    │   └── webhooks.py                  # /api/webhooks/*
    └── schemas/                         # Request/Response DTOs
        ├── checkout.py
        ├── terminal.py
        ├── tools.py
        ├── auth.py
        └── webhook.py
```

---

## 🔐 Authentication

- **Provider:** Supabase (JWT verification via `SUPABASE_JWT_SECRET`)
- **Coverage:** All endpoints except `POST /api/webhooks/adyen/{user_id}` require `Authorization: Bearer <supabase_jwt>`
- **Config storage:** Adyen credentials stored per-user in `adyen_configs` Supabase table

### Roles

| Role    | Config write access | Webhook retention |
|---------|--------------------|--------------------|
| `admin` | ✅ Yes              | 5 days             |
| `im`    | ✅ Yes              | 3 days             |
| `user`  | ❌ No               | 3 days             |

Roles are stored in the `profiles` Supabase table and retrieved at runtime.

---

## 🗄️ Webhooks

- **Ingest:** `POST /api/webhooks/adyen/{user_id}` — no auth required, receives Adyen standard notifications
- **Routing:** `user_id` comes from the URL path parameter — no Adyen payload lookup needed
- **Retention:** Computed at insert time via `expires_at` (admin: 5 days, im/user: 3 days)
- **Cleanup:** `expires_at` filter on all reads + pg_cron daily `DELETE` at 03:00 UTC
- **Migration:** `migrations/001_create_webhooks_table.sql` — auto-applied on startup

---

## ⚙️ Setup

### 1. Clone & create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your credentials
```

| Variable | Description |
|----------|-------------|
| `ADYEN_API_KEY` | Customer Area → Developers → API credentials |
| `ADYEN_MERCHANT_ACCOUNT` | Your merchant account name |
| `ADYEN_CLIENT_KEY` | Served to the frontend via `/api/config/client` |
| `ADYEN_ENVIRONMENT` | `test` or `live` |
| `ADYEN_HMAC_KEY` | HMAC key for webhook signature validation |
| `CORS_ORIGINS` | Comma-separated frontend origins (e.g. `http://localhost:3000`) |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for server-side Supabase access |
| `SUPABASE_JWT_SECRET` | JWT secret for token verification |
| `SUPABASE_DATABASE_URL` | Transaction mode pooler URL (port 6543) — migration runner only |

### 3. Run

```bash
uvicorn app.main:app --reload --port 8000
```

API docs at http://localhost:8000/docs

---

## 🗂️ Epic Mapping

| Epic branch                             | Features                                                        |
|-----------------------------------------|-----------------------------------------------------------------|
| `valedorsinho/epic/online-checkout`     | Checkout flows, payload validator, vertical suggestions         |
| `valedorsinho/epic/terminal-payments`   | Cloud Terminal API payments, merchants, stores, terminals       |
| `valedorsinho/epic/fleet-management`    | Terminal fleet management, reassign                             |
| `valedorsinho/epic/webhooks`            | Webhook ingestion, viewer, HMAC signature validation            |
| `valedorsinho/epic/tools-and-setup`     | Config, auth, environment setup                                 |

Feature branches follow the same project prefix:
`valedorsinho/feature/<description>` — branched from its parent epic.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for full branching and PR rules.

---

## 💡 Key Implementation Notes

- **Amount units:** Online checkout = minor units (e.g. `1000` = €10.00); Terminal payments = major units.
- **Webhook routing:** `user_id` comes from the URL path — no Adyen payload parsing needed for routing.
- **Orphan webhooks:** If `user_id` is not in `profiles`, the webhook is stored with a default 3-day retention.
- **Migrations:** SQL files in `migrations/` are auto-applied on startup and tracked in a `_migrations` Supabase table.
