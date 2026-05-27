---
description: Update the stored project context memory after a commit or significant structural change
---

# Update Project Context

Run this workflow after making a commit or when the project structure has changed significantly (new modules, renamed files, new blueprints, new routes, etc.).

## Steps

1. Review recent changes to understand what was modified:
   // turbo
   ```bash
   git log -1 --stat
   ```

2. Re-read the key structural files to capture any changes:
   - `checkout/__init__.py` — blueprint registrations
   - `checkout/config.py` — env vars, Adyen client config
   - `checkout/adyen_models.py` — Pydantic models
   - `checkout/contexts.py` — template context dataclasses
   - `checkout/checkout_helpers.py` — shared helpers
   - `checkout/integrations.py` — integration registry
   - `checkout/pages.py` — checkout page routes
   - `checkout/advanced_api.py` — Advanced API endpoints
   - `checkout/sessions_api.py` — Sessions API endpoints
   - `homepage/pages.py` — homepage routes
   - `setup/pages.py` — setup routes
   - `payload_validator/pages.py` and `payload_validator/api.py` — validator routes
   - `payload_suggested/pages.py` — suggested payload routes
   - `nfc_formatter/pages.py` — NFC formatter routes
   - `terminal_fleet/pages.py` and `terminal_fleet/api.py` — terminal fleet routes
   - `terminal_payments/pages.py` and `terminal_payments/api.py` — terminal payments routes & Management API proxies
   - `requirements.txt` — dependencies
   - Any **new** Python modules or blueprint files

3. Check for new files or directories that weren't previously tracked:
   // turbo
   ```bash
   find . -name '*.py' -not -path './.venv/*' -not -path './.git/*' | sort
   ```

4. **Update the existing memory** titled "Valedorsinho – Full Project Context" (ID: `34da21ef-c6b2-4168-818c-4e23643b71dc`) with:
   - Any new or removed modules/blueprints
   - New or changed routes
   - New or updated Pydantic models or dataclasses
   - Dependency changes in `requirements.txt`
   - New environment variables
   - Any new architectural patterns

   Use the `update` action on the memory, not `create`, to avoid duplicates.

5. Confirm to the user what changed in the context.
