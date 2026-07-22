---
description: Update the stored project context memory after a commit or significant structural change
---

# Update Project Context

Run this workflow after making a commit or when the project structure has changed significantly (new modules, renamed files, new routes, new migrations, etc.).

## Steps

1. Review recent changes to understand what was modified:
   ```bash
   git log -1 --stat
   ```

2. Re-read the key structural files to capture any changes:

   **App factory & routing**
   - `app/main.py` — router registrations, lifespan hooks

   **Domain layer**
   - `app/domain/models/auth.py` — UserRole, UserProfile, AdyenCredentials
   - `app/domain/models/checkout.py` — Amount, PaymentRequest, SessionsRequest, etc.
   - `app/domain/models/terminal.py` — DecodedTerminalResponse, PaymentSummaryField
   - `app/domain/models/webhook.py` — WebhookEvent
   - `app/domain/verticals.py` — merchant vertical definitions (VERTICALS list)

   **Ports (interfaces)**
   - `app/ports/auth_port.py`
   - `app/ports/checkout_port.py`
   - `app/ports/terminal_port.py`
   - `app/ports/management_port.py`
   - `app/ports/validator_port.py`
   - `app/ports/webhook_port.py`

   **Use cases**
   - `app/use_cases/auth_service.py`
   - `app/use_cases/checkout_service.py`
   - `app/use_cases/terminal_payment_service.py`
   - `app/use_cases/terminal_fleet_service.py`
   - `app/use_cases/tools_service.py`
   - `app/use_cases/webhook_service.py`

   **Adapters**
   - `app/adapters/supabase_adapter.py` — AuthGateway → Supabase REST + JWT
   - `app/adapters/checkout_adapter.py` — CheckoutGateway → Adyen SDK
   - `app/adapters/management_adapter.py` — ManagementGateway → Adyen SDK
   - `app/adapters/terminal_adapter.py` — TerminalGateway → Adyen Terminal Cloud API
   - `app/adapters/terminal_decoder.py` — pure decoding utilities
   - `app/adapters/validator_adapter.py` — PayloadValidator → Adyen OpenAPI spec
   - `app/adapters/webhook_adapter.py` — WebhookGateway → Supabase REST

   **API layer**
   - `app/api/config.py` — env var constants
   - `app/api/dependencies.py` — FastAPI DI wiring
   - `app/api/routers/` — one file per domain
   - `app/api/schemas/` — Pydantic request/response DTOs

   **Database**
   - `migrations/*.sql` — SQL migration files
   - `app/db/migrations.py` — migration runner

   **Dependencies**
   - `requirements.txt`

3. Check for new Python files not previously tracked:
   ```bash
   find app/ migrations/ -name '*.py' -o -name '*.sql' | sort
   ```

4. Update the existing memory titled "Valedorsinho – Full Project Context" (ID: `34da21ef-c6b2-4168-818c-4e23643b71dc`) with:
   - New or removed modules / routes
   - New domain models or ports
   - New or changed environment variables
   - New migration files
   - Dependency changes in `requirements.txt`
   - Architectural changes

   Use the `update` action — not `create` — to avoid duplicates.

5. Confirm to the user what changed in the context.
