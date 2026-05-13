<h1> <center> Valedorsinho </center></h1>
<center>Esto es de valedores.</center>
<br>
<br>

# <center> Adyen Checkout – Python / Flask</center>

A minimal Flask application that shows how to integrate Adyen's **Drop-in Component** and run a **native 3DS2** (in-browser) authentication flow.

## Flow overview

```
Browser                     Flask (app.py)              Adyen API
──────                      ──────────────              ─────────
GET /                  →    render checkout.html
GET /api/paymentMethods →   POST /paymentMethods    →   payment method list
                             ←───────────────────────────
[shopper fills card]
onSubmit fires         →    POST /api/payments       →   POST /payments
                             ←  action{type:threeDS2} ←──
Drop-in renders 3DS2
fingerprint/challenge
onAdditionalDetails    →    POST /api/payments/details → POST /payments/details
                             ←  resultCode:Authorised  ←─
handleFinalResult      →    GET /result?status=success
```

If the card issuer does not support native 3DS2, Adyen falls back to a full-page redirect to the issuer's ACS. After authentication the shopper is sent back to `/api/handleShopperRedirect`.
<br><br>
# <center>Setup</center>

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

Open http://localhost:8080 in your browser.

## Test cards

Use Adyen's test card numbers to trigger different 3DS2 scenarios:
https://docs.adyen.com/development-resources/testing/test-card-numbers

| Scenario               | Card number         | Expiry   | CVC |
|------------------------|---------------------|----------|-----|
| 3DS2 native challenge  | 4917 6100 0000 0000 | any future | any |
| Frictionless (no UX)   | 5454 5454 5454 5454 | any future | any |
| Refused                | 4111 1111 1111 1111 | any future | any |

## Project structure

```
.
├── app.py                  # Flask server – all API routes
├── requirements.txt
├── .env.example
└── templates/
    ├── checkout.html       # Drop-in Component + 3DS2 JS logic
    └── result.html         # Success / failure result page
```
