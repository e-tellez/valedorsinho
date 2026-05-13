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

## Flow overview

```
Browser                        Flask server                 Adyen API
───────                        ────────────                 ─────────
1. GET /                  →    render order form
2. POST /                 →    validate & store in session
3. GET /implementations   →    render integration selector
4. GET /dropin/checkout   →    render Drop-in page
5. GET /api/paymentMethods →   POST /paymentMethods     →   payment method list
                                                              (incl. stored cards)
6. [shopper fills card / picks stored card]
   onSubmit               →    POST /api/payments        →   POST /payments
                                ← action{type:threeDS2}  ←──
7. Drop-in renders 3DS2
   fingerprint/challenge
   onAdditionalDetails    →    POST /api/payments/details → POST /payments/details
                                ← resultCode:Authorised   ←─
8. POST /result/store     →    store result in session
9. GET /result            →    render result page & clear session
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

## Tokenisation

Tokenisation uses `recurringProcessingModel: CardOnFile` with shopper consent:

1. Enter a username (used as `shopperReference`)
2. Pay with a new card — a "Save for my next payment" checkbox appears
3. If the shopper consents, we ask Adyen to tokenise the card
4. On the next visit with the same username, stored cards appear in the Drop-in or Card Component

New cards should be sent with `shopperInteraction: Ecommerce`; stored cards with `ContAuth`.

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
│   ├── pages.py                    # Blueprint: HTML-serving routes
│   └── api.py                      # Blueprint: JSON API + redirect handlers
├── templates/
│   ├── pages/
│   │   ├── order.html              # Step 1 – shopper & amount form
│   │   ├── implementation_index.html # Step 2 – integration selector
│   │   ├── dropin.html             # Step 3 – Drop-in checkout
│   │   ├── card_component.html     # Step 3 – Card Component checkout
│   │   └── result.html             # Payment result page
│   └── errors/
│       └── 404.html
└── static/
    ├── css/
    └── js/
        ├── dropin.js               # Drop-in initialisation & 3DS2 handling
        └── card_component.js       # Card Component initialisation
```
