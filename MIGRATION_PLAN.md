# Migration Plan: FastAPI Backend + Next.js 14 Frontend

## Architecture Overview

```
┌─────────────────────┐         ┌──────────────────────┐
│   Next.js 14 (FE)   │  HTTP   │   FastAPI (BE)       │
│   localhost:3000     │ ──────→ │   localhost:8000     │
│                      │  JSON   │                      │
│  - React pages       │ ←────── │  - Adyen API calls   │
│  - Adyen Web SDK     │         │  - Terminal API      │
│  - Tailwind CSS      │         │  - Session state     │
│  - Client routing    │         │  - Validation        │
└─────────────────────┘         └──────────────────────┘
```

- **Backend (Python)**: All Adyen SDK calls, Terminal API Cloud, Management API proxies, payload validation, session management. Flask → **FastAPI**.
- **Frontend (TypeScript)**: All UI rendering, Adyen Web SDK (Drop-in, Card Component), user interaction. Jinja2 + vanilla JS → **Next.js 14 App Router + React**.

---

## What Stays in Python (FastAPI)

Everything that currently lives in Flask blueprints' API routes and server-side logic:

| Current Python Module | FastAPI Router | Stays Because |
|---|---|---|
| `checkout/config.py` | `app/core/config.py` | Adyen Python SDK client, env vars |
| `checkout/adyen_models.py` | `app/models/checkout.py` | Pydantic models — FastAPI is built on Pydantic |
| `checkout/advanced_api.py` | `app/routers/checkout.py` | Adyen /payments, /paymentMethods, /payments/details |
| `checkout/sessions_api.py` | `app/routers/checkout.py` | Adyen /sessions |
| `checkout/checkout_helpers.py` | `app/core/helpers.py` | Reference generation, country/currency map |
| `terminal_payments/api.py` | `app/routers/terminal_payments.py` | Terminal API Cloud, Management API proxies |
| `terminal_fleet/api.py` | `app/routers/terminal_fleet.py` | Management API terminal listing, reassignment |
| `payload_validator/validator.py` | `app/services/validator.py` | OpenAPI spec fetching + jsonschema validation |
| `payload_suggested/verticals.py` | `app/data/verticals.py` | Static vertical definitions (could also move to FE) |
| `terminal_payments/pages.py` | `app/services/terminal_decoder.py` | `_decode_additional_response`, `_extract_payment_summary` |

### What Moves to Frontend (Next.js)

Everything that currently lives in Jinja2 templates, static CSS/JS, and Flask page routes:

| Current | Next.js |
|---|---|
| `templates/base.html` | `app/layout.tsx` |
| `templates/pages/*.html` | `app/**/page.tsx` (React components) |
| `templates/macros.html` | React components (`StepIndicator`, `PreviewCard`, etc.) |
| `static/css/*.css` | Tailwind CSS classes + `globals.css` |
| `static/js/*.js` | React components with hooks (`useEffect`, `useState`) |
| Flask `render_template()` page routes | Eliminated — Next.js handles routing via file system |

### What Gets Eliminated

| Current | Why |
|---|---|
| Flask page routes (`checkout/pages.py`, `homepage/pages.py`, etc.) | Next.js file-system routing replaces them |
| `checkout/contexts.py` (dataclasses for template context) | React components receive data via props/hooks |
| `checkout/integrations.py` (decorator registry) | Static config array in frontend |
| `require_session` decorator | Middleware or route guards in Next.js |
| Jinja2 macros | React components |

---

## Route Mapping

### FastAPI API Routes (all under `/api/`)

| Flask Route | FastAPI Route | Method | Purpose |
|---|---|---|---|
| `/api/paymentMethods` | `/api/checkout/payment-methods` | GET | Adyen /paymentMethods |
| `/api/payments` | `/api/checkout/payments` | POST | Adyen /payments |
| `/api/payments/details` | `/api/checkout/payments/details` | POST | Adyen /payments/details |
| `/api/sessions` | `/api/checkout/sessions` | POST | Adyen /sessions |
| `/api/disable` | `/api/checkout/disable` | POST | Disable stored payment method |
| `/result/store` | `/api/checkout/result` | POST | Store payment result in session |
| `/dropin/handleShopperRedirect` | `/api/checkout/redirect` | GET,POST | Handle 3DS redirect |
| `/sessions/handleShopperRedirect` | `/api/checkout/sessions/redirect` | GET | Handle sessions 3DS redirect |
| `/terminal-payments/api/merchants` | `/api/terminal/merchants` | GET | List merchants |
| `/terminal-payments/api/stores` | `/api/terminal/stores` | GET | List stores |
| `/terminal-payments/api/terminals` | `/api/terminal/terminals` | GET | List terminals |
| `/terminal-payments/api/make-payment` | `/api/terminal/make-payment` | POST | Terminal API Cloud payment |
| `/terminal-fleet/api/terminals` | `/api/fleet/terminals` | GET | List terminals (fleet) |
| `/terminal-fleet/api/stores` | `/api/fleet/stores` | GET | List stores (fleet) |
| `/terminal-fleet/api/reassign` | `/api/fleet/reassign` | POST | Reassign terminals |
| `/api/validate-payload` | `/api/tools/validate-payload` | POST | Validate /payments payload |
| — | `/api/tools/verticals` | GET | Return vertical definitions |
| — | `/api/config/client` | GET | Return client_key + environment |

**New endpoints** (`/api/config/client`, `/api/tools/verticals`): The frontend needs `ADYEN_CLIENT_KEY` and `ADYEN_ENVIRONMENT` to initialize the Adyen Web SDK. Instead of `NEXT_PUBLIC_` env vars, the backend serves them — keeping all config in one place.

### Next.js Frontend Pages

| Flask Page Route | Next.js Page | Component Type |
|---|---|---|
| `GET /` | `app/page.tsx` | Server |
| `GET /checkout` | `app/checkout/page.tsx` | Server |
| `GET,POST /order` | `app/checkout/order/page.tsx` | Client |
| `GET /implementations` | `app/checkout/implementations/page.tsx` | Client |
| `GET /components/checkout` | `app/checkout/components/page.tsx` | Client |
| `GET /dropin/checkout` | `app/checkout/dropin/page.tsx` | Client |
| `GET /sessions/dropin/checkout` | `app/checkout/sessions/dropin/page.tsx` | Client |
| `GET /sessions/components/checkout` | `app/checkout/sessions/components/page.tsx` | Client |
| `GET /manage-payments` | `app/checkout/manage-payments/page.tsx` | Client |
| `GET /result` | `app/checkout/result/page.tsx` | Client |
| `GET /terminal-payments/` | `app/terminal-payments/page.tsx` | Client |
| `GET /terminal-payments/make-payment` | `app/terminal-payments/make-payment/page.tsx` | Client |
| `GET /terminal-payments/nfc` | `app/terminal-payments/nfc/page.tsx` | Client |
| `GET /terminal-payments/card-acquisition` | `app/terminal-payments/card-acquisition/page.tsx` | Client |
| `GET /terminal-payments/auth-capt` | `app/terminal-payments/auth-capt/page.tsx` | Client |
| `GET,POST /terminal-payments/payment-result` | `app/terminal-payments/payment-result/page.tsx` | Client |
| `GET /terminal-fleet/` | `app/terminal-fleet/page.tsx` | Client |
| `GET /setup/` | `app/setup/page.tsx` | Server |
| `GET /payload-validator/` | `app/payload-validator/page.tsx` | Client |
| `GET /payload-suggested/` | `app/payload-suggested/page.tsx` | Client |
| `GET /nfc-formatter/` | `app/nfc-formatter/page.tsx` | Client |
| `GET /management-api/` | `app/management-api/page.tsx` | Server |

---

## Proposed Directory Structure

### Backend (`backend/`)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                                   # FastAPI app factory, CORS, router registration
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                             # Settings (from checkout/config.py), Adyen client
│   │   └── helpers.py                            # generate_reference(), COUNTRY_CURRENCY_MAP
│   ├── models/
│   │   ├── __init__.py
│   │   └── checkout.py                           # Pydantic models (from adyen_models.py)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── checkout.py                           # /api/checkout/* endpoints
│   │   ├── terminal_payments.py                  # /api/terminal/* endpoints
│   │   ├── terminal_fleet.py                     # /api/fleet/* endpoints
│   │   └── tools.py                              # /api/tools/* (validator, verticals)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── validator.py                          # OpenAPI spec validator (from payload_validator/)
│   │   └── terminal_decoder.py                   # AdditionalResponse decoder + payment summary
│   └── data/
│       └── verticals.py                          # Vertical definitions (from payload_suggested/)
├── .env
├── .env.example
└── requirements.txt
```

### Frontend (`frontend/`)

```
frontend/
├── app/
│   ├── layout.tsx                                # Root layout (replaces base.html)
│   ├── page.tsx                                  # Dashboard
│   ├── globals.css                               # Global styles
│   ├── not-found.tsx                             # 404 page
│   │
│   ├── checkout/
│   │   ├── layout.tsx                            # Shared checkout layout (step indicator)
│   │   ├── page.tsx                              # Choose flow
│   │   ├── order/
│   │   │   └── page.tsx                          # Order form
│   │   ├── implementations/
│   │   │   └── page.tsx                          # Integration index
│   │   ├── components/
│   │   │   └── page.tsx                          # Card Component
│   │   ├── dropin/
│   │   │   └── page.tsx                          # Drop-in
│   │   ├── sessions/
│   │   │   ├── dropin/
│   │   │   │   └── page.tsx                      # Sessions Drop-in
│   │   │   └── components/
│   │   │       └── page.tsx                      # Sessions Card Component
│   │   ├── manage-payments/
│   │   │   └── page.tsx                          # Manage stored payments
│   │   └── result/
│   │       └── page.tsx                          # Payment result
│   │
│   ├── terminal-payments/
│   │   ├── page.tsx                              # Terminal selector
│   │   ├── make-payment/
│   │   │   └── page.tsx                          # Make payment
│   │   ├── nfc/
│   │   │   └── page.tsx
│   │   ├── card-acquisition/
│   │   │   └── page.tsx
│   │   ├── auth-capt/
│   │   │   └── page.tsx
│   │   └── payment-result/
│   │       └── page.tsx                          # Terminal payment result
│   │
│   ├── terminal-fleet/
│   │   └── page.tsx                              # Fleet manager
│   │
│   ├── setup/
│   │   └── page.tsx                              # Environment setup
│   │
│   ├── payload-validator/
│   │   └── page.tsx                              # Payload validator
│   │
│   ├── payload-suggested/
│   │   └── page.tsx                              # Payload generator
│   │
│   ├── nfc-formatter/
│   │   └── page.tsx                              # NFC formatter
│   │
│   └── management-api/
│       └── page.tsx                              # Management API explorer
│
├── components/
│   ├── ui/                                       # shadcn/ui components
│   ├── checkout/
│   │   ├── AdyenDropin.tsx                       # Adyen Drop-in wrapper
│   │   ├── AdyenCardComponent.tsx                # Card Component wrapper
│   │   ├── OrderForm.tsx                         # Order form
│   │   └── StepIndicator.tsx                     # Step indicator
│   ├── terminal/
│   │   ├── TerminalSelector.tsx                  # Cascading merchant→store→terminal
│   │   ├── PayloadPreview.tsx                    # JSON payload preview
│   │   └── PaymentSummary.tsx                    # Payment result summary grid
│   └── shared/
│       ├── BackButton.tsx                        # btn-back component
│       ├── PreviewCard.tsx                       # Preview card
│       └── DashboardCard.tsx                     # Dashboard tool cards
│
├── lib/
│   ├── api.ts                                    # Fetch wrapper for FastAPI calls
│   ├── types.ts                                  # Shared TypeScript types
│   └── constants.ts                              # Integration registry, country/currency map
│
├── hooks/
│   ├── useCheckoutConfig.ts                      # Fetch client_key + environment from backend
│   └── useAdyen.ts                               # Adyen Web SDK initialization
│
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## Key Decisions

### 1. Session Management

**Current**: Flask cookie-based `session` stores checkout state (shopper_reference, amount, currency, country_code, payment_data, etc.).

**FastAPI approach**: Two options —

| Option | How | Pros | Cons |
|---|---|---|---|
| **A) Stateless (recommended)** | Frontend holds checkout state in React Context / Zustand. Passes it in each API request body. | Simple, scalable, no session store needed | Frontend must manage state; slightly larger request bodies |
| **B) Server sessions** | FastAPI stores sessions in Redis or signed cookies via `starsessions` | Familiar pattern, minimal frontend changes | Adds infrastructure (Redis), CORS cookie complexity |

**Recommendation**: **Option A — stateless**. The checkout flow state (`amount`, `currency`, `country_code`, `shopper_reference`) is small and non-sensitive. The frontend passes it with each API call. `payment_data` (for 3DS) is the only server-critical value — store it temporarily in a short-lived cache (in-memory dict or Redis) keyed by `order_ref`.

### 2. CORS Configuration

FastAPI and Next.js run on different ports during development. FastAPI needs:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

In production, either serve both from the same domain via a reverse proxy (Nginx/Caddy) or set the correct production origin.

### 3. Adyen Web SDK Loading

**Current**: Jinja2 macros inject `<script>` and `<link>` tags for the Adyen Web SDK.

**Next.js**: Use `next/script` for the SDK JS and import CSS in the layout:

```tsx
// app/checkout/layout.tsx
import Script from "next/script";

export default function CheckoutLayout({ children }) {
  return (
    <>
      <link rel="stylesheet" href="https://checkoutshopper-test.adyen.com/checkoutshopper/sdk/5.67.0/adyen.css" />
      <Script src="https://checkoutshopper-test.adyen.com/checkoutshopper/sdk/5.67.0/adyen.js" strategy="beforeInteractive" />
      {children}
    </>
  );
}
```

Alternatively, install `@adyen/adyen-web` via npm for tighter React integration (recommended for long-term).

### 4. 3DS Redirect Handling

**Current**: Flask renders `redirect_result.html` / `sessions_redirect.html` — tiny intermediate pages that store the Adyen response in `sessionStorage` then navigate to `/result`.

**Next.js**: The redirect handler pages (`/checkout/redirect`, `/checkout/sessions/redirect`) become client components that:
1. Read `redirectResult` from URL search params
2. Call FastAPI `/api/checkout/redirect?redirectResult=...`
3. FastAPI calls Adyen `/payments/details` and returns the result
4. Frontend stores result in React state / context and navigates to `/checkout/result`

### 5. Styling

| Current | Next.js |
|---|---|
| `base.css` + per-page CSS files | `globals.css` + **Tailwind CSS** utility classes |
| `.btn-back`, `.btn-primary`, `.btn-secondary` | shadcn/ui `<Button variant="...">` component |
| Jinja2 macros for repeated UI | React components (`<StepIndicator>`, `<PreviewCard>`) |
| Per-page CSS files | Component-scoped via Tailwind; no separate CSS files needed |

### 6. Python Dependencies Change

| Remove | Keep | Add |
|---|---|---|
| `Flask` | `Adyen` | `fastapi` |
| `Jinja2` | `pydantic` | `uvicorn` |
| `Werkzeug` | `requests` | `python-multipart` |
| `itsdangerous` | `jsonschema` | `starlette` (comes with FastAPI) |
| `blinker` | `certifi` | |
| `MarkupSafe` | | |
| `click` | | |

---

## Flask → FastAPI Translation Cheat Sheet

### Route Definitions

```python
# Flask
@bp.route("/api/payments", methods=["POST"])
def payments():
    body = request.get_json()
    ...
    return jsonify(response_body)

# FastAPI
@router.post("/api/checkout/payments")
async def payments(body: PaymentRequestBody):
    ...
    return response_body  # FastAPI auto-serializes dicts/models to JSON
```

### Query Parameters

```python
# Flask
merchant_id = request.args.get("merchantId", "")

# FastAPI
@router.get("/api/terminal/stores")
async def list_stores(merchant_id: str = Query(alias="merchantId")):
    ...
```

### Error Responses

```python
# Flask
return jsonify({"error": str(error)}), 500

# FastAPI
from fastapi import HTTPException
raise HTTPException(status_code=500, detail=str(error))
```

### Pydantic Models (almost no change)

```python
# Current (already Pydantic) — works in FastAPI as-is
class PaymentRequest(AdyenModel):
    merchant_account: str
    reference: str
    amount: Amount
    ...
```

---

## Migration Phases

### Phase 1: FastAPI Backend Scaffold
1. Create `backend/` directory with FastAPI project structure
2. Port `checkout/config.py` → `app/core/config.py` (remove Flask-specific parts)
3. Port `checkout/adyen_models.py` → `app/models/checkout.py` (no changes needed)
4. Port `checkout/checkout_helpers.py` → `app/core/helpers.py` (remove Flask session/redirect)
5. Create `app/main.py` with CORS middleware and router registration
6. Port checkout API endpoints: `/api/checkout/payment-methods`, `/payments`, `/payments/details`, `/sessions`
7. Port terminal API endpoints: `/api/terminal/merchants`, `/stores`, `/terminals`, `/make-payment`
8. Port fleet API endpoints: `/api/fleet/terminals`, `/stores`, `/reassign`
9. Port tools endpoints: `/api/tools/validate-payload`, `/api/tools/verticals`
10. Port redirect handlers: `/api/checkout/redirect`, `/api/checkout/sessions/redirect`
11. Add `/api/config/client` endpoint (returns client_key + environment)
12. Write `requirements.txt` for backend

### Phase 2: Next.js Frontend Scaffold
13. `npx create-next-app@14 frontend` with TypeScript, Tailwind, App Router
14. Create `lib/api.ts` — fetch wrapper with FastAPI base URL
15. Create `lib/types.ts` — TypeScript types matching Pydantic models
16. Create `lib/constants.ts` — integration registry, country/currency map
17. Create `hooks/useCheckoutConfig.ts` and `hooks/useAdyen.ts`
18. Create shared components: `BackButton`, `DashboardCard`, `StepIndicator`, `PreviewCard`
19. Create `app/layout.tsx` (port `base.html`)
20. Create `app/globals.css` (port `base.css`)

### Phase 3: Dashboard & Static Pages
21. Port dashboard (`app/page.tsx`)
22. Port setup page (`app/setup/page.tsx`)
23. Port management API page (`app/management-api/page.tsx`)
24. Port 404 page (`app/not-found.tsx`)

### Phase 4: Checkout Flow
25. Create `CheckoutContext` (React Context for checkout state)
26. Port choose flow → order → implementations pages
27. Create `AdyenDropin.tsx` and `AdyenCardComponent.tsx` client components
28. Port Drop-in page (advanced + sessions variants)
29. Port Card Component page (advanced + sessions variants)
30. Port redirect handler pages
31. Port result page
32. Port manage-payments page

### Phase 5: Terminal Payments
33. Create `TerminalSelector.tsx` (cascading dropdowns)
34. Port terminal payments index page
35. Port make-payment page with `PayloadPreview.tsx`
36. Port payment-result page with `PaymentSummary.tsx`
37. Port NFC, card-acquisition, auth-capt placeholder pages

### Phase 6: Tools
38. Port terminal fleet page
39. Port payload validator page
40. Port payload suggested page
41. Port NFC formatter page

### Phase 7: Integration & Polish
42. Set up `next.config.js` API proxy (rewrite `/api/*` to FastAPI in dev)
43. Verify all Adyen Web SDK integrations
44. Test 3DS2 redirect flows end-to-end
45. Test Terminal API Cloud payments
46. Production deployment config (reverse proxy, env vars)
47. Remove Flask files from project

---

## Environment Variables

### Backend (`backend/.env`)

```
ADYEN_API_KEY=...
ADYEN_MERCHANT_ACCOUNT=...
ADYEN_CLIENT_KEY=...
ADYEN_ENVIRONMENT=test
CORS_ORIGINS=http://localhost:3000
```

### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Only one env var needed on the frontend — everything else comes from the backend via `/api/config/client`.

---

## Frontend Dependencies (package.json)

```json
{
  "dependencies": {
    "next": "^14.2",
    "react": "^18.3",
    "react-dom": "^18.3",
    "@adyen/adyen-web": "^5.67.0"
  },
  "devDependencies": {
    "typescript": "^5.5",
    "@types/node": "^22",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "tailwindcss": "^3.4",
    "postcss": "^8.4",
    "autoprefixer": "^10.4"
  }
}
```

## Backend Dependencies (requirements.txt)

```
fastapi>=0.115
uvicorn>=0.34
python-multipart>=0.0.18
Adyen>=15.0.1
pydantic>=2.13
requests>=2.32
jsonschema>=4.23
certifi>=2024.8
```

---

## Dev Workflow

```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev    # localhost:3000
```

Next.js `next.config.js` rewrites to avoid CORS in development:

```js
// frontend/next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};
```

This lets the frontend call `/api/checkout/payments` as a same-origin request during development. In production, a reverse proxy (Nginx/Caddy) handles the same routing.
