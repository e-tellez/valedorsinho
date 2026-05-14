<h1> <center> Valedorsinho </center></h1>
<center>Esto es de valedores.</center>
<br>
<br>

# <center> Adyen Checkout – Python / Flask</center>

A Flask application that implements Adyen's **Drop-in** and **Card Component** integrations and covers **native 3DS2** authentication and **tokenisation**.

## Features

- **Drop-in** – pre-built UI with all available payment methods configured in your account
- **Card Component** – card-only fields with full UI control
- **Native 3DS2** – in-browser fingerprint and challenge flows
- **Tokenisation** – save cards for returning shoppers (with shopper consent)
- **Guest checkout** – pay without creating an account (no tokenisation, no stored cards)

## Flow overview

The checkout has **4 steps**:

| Step | Route | Description |
|------|-------|-------------|
| 1 | `GET /` | Choose between **Guest** and **Account** checkout |
| 2 | `GET /order` → `POST /order` | Enter order details (+ username for account flow) |
| 3 | `GET /implementations` | Choose integration type (Drop-in / Components) |
| 4 | `GET /dropin/checkout` or `GET /components/checkout` | Pay |

### Guest vs Account

- **Guest** – no `shopperReference` is sent to Adyen; tokenisation fields (`storePaymentMethod`, `recurringProcessingModel`, `shopperInteraction`) are omitted; the "Save for my next payment" checkbox is hidden.
- **Account** – a username is collected and used as `shopperReference`; tokenisation is enabled with `recurringProcessingModel: CardOnFile`.

### Sequence diagram

```
Browser                        Flask server                 Adyen API
───────                        ────────────                 ─────────
1. GET /                  →    render flow choice
2. GET /order?flow=…      →    render order form
3. POST /order            →    validate & store in session
4. GET /implementations   →    render integration selector
5. GET /dropin/checkout   →    render Drop-in page
6. GET /api/paymentMethods →   POST /paymentMethods     →   payment method list
                                                              (incl. stored cards for account)
7. [shopper fills card / picks stored card]
   onSubmit               →    POST /api/payments        →   POST /payments
                                ← action{type:threeDS2}  ←──
8. Drop-in renders 3DS2
   fingerprint/challenge
   onAdditionalDetails    →    POST /api/payments/details → POST /payments/details
                                ← resultCode:Authorised   ←─
9. POST /result/store     →    store result in session
10. GET /result           →    render result page & clear session
```

If the issuer does not support native 3DS2, Adyen falls back to a redirect. After authentication the shopper returns to `/dropin/handleShopperRedirect`.

## Setup

### 1. Clone & create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your Adyen credentials
```

You need:
- **ADYEN_API_KEY** – from Customer Area → Developers → API credentials
- **ADYEN_MERCHANT_ACCOUNT** – your merchant account name
- **ADYEN_CLIENT_KEY** – from the same API credentials page (Client Keys tab)
- **ADYEN_ENVIRONMENT** – `test` for testing, `live` for production

### 3. Run

```bash
python app.py
```

Open http://localhost:3000 in your browser or configure app.py to use a different port.

## Test cards

Use Adyen's test card numbers to trigger different 3DS2 scenarios:
https://docs.adyen.com/development-resources/testing/test-card-numbers

## Tokenisation (Account flow only)

Tokenisation uses `recurringProcessingModel: CardOnFile` with shopper consent:

1. Choose **Account** on step 1
2. Enter a username (used as `shopperReference`)
3. Pay with a new card — a "Save for my next payment" checkbox appears
4. If the shopper consents, we ask Adyen to tokenise the card
5. On the next visit with the same username, stored cards appear in the Drop-in or Card Component

New cards are sent with `shopperInteraction: Ecommerce`; stored cards with `ContAuth`.

Guest payments skip all of this — no reference, no checkbox, no stored cards.

## Project structure

```
.
├── app.py                          # Entry point
├── requirements.txt
├── .env.example
├── checkout/
│   ├── __init__.py                 # App factory – registers blueprints
│   ├── config.py                   # Adyen client, env vars, SSL fix
│   ├── helpers.py                  # Shared constants & utilities
│   ├── integrations.py             # @register_integration decorator & registry
│   ├── models.py                   # Pydantic models for Adyen API requests
│   ├── pages.py                    # Blueprint: HTML-serving routes
│   └── api.py                      # Blueprint: JSON API + redirect handlers
├── templates/
│   ├── pages/
│   │   ├── choose_flow.html        # Step 1 – guest vs account
│   │   ├── order.html              # Step 2 – shopper & amount form
│   │   ├── implementation_index.html # Step 3 – integration selector
│   │   ├── dropin.html             # Step 4 – Drop-in checkout
│   │   ├── card_component.html     # Step 4 – Card Component checkout
│   │   └── result.html             # Payment result page
│   └── errors/
│       └── 404.html
└── static/
    ├── css/
    └── js/
        ├── adyen_api.js            # Shared API helpers (fetch, payments, result)
        ├── dropin.js               # Drop-in initialisation & 3DS2 handling
        └── card_component.js       # Card Component initialisation
```
