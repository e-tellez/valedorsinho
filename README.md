<h1> <center> Valedorsinho </center></h1>
<center>Esto es de valedores.</center>
<br>
<br>

# Adyen Integration Backend — FastAPI

Backend-only API for Adyen integration demos. Built with **FastAPI** and **hexagonal architecture**. The frontend lives in a separate repository.

## Features

- **Online Checkout** — Advanced flow (`/payments`, `/payments/details`) and Sessions flow (`/sessions`)
- **Terminal Payments** — Cloud Terminal API with cascading terminal selector
- **Terminal Fleet Management** — List, search, and reassign terminals
- **Payload Validator** — Validate `/payments` payloads against the Adyen OpenAPI spec
- **Vertical Suggestions** — Pre-built payloads for retail, hospitality, digital goods, etc.
- **Tokenisation** — Save cards for returning shoppers (`CardOnFile`)

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
- **ADYEN_API_KEY** — from Customer Area → Developers → API credentials
- **ADYEN_MERCHANT_ACCOUNT** — your merchant account name
- **ADYEN_CLIENT_KEY** — served to the frontend via `/api/config/client`
- **ADYEN_ENVIRONMENT** — `test` or `live`
- **CORS_ORIGINS** — comma-separated frontend origins (default `http://localhost:3000`)

### 3. Run

```bash
uvicorn app.main:app --reload --port 8000
```

API docs at http://localhost:8000/docs

## API Contract

See [API_CONTRACT.md](API_CONTRACT.md) for the full endpoint reference to sync with the frontend repo.

## Architecture — Hexagonal

```
app/
├── main.py                              # FastAPI app factory
│
├── domain/                              # CORE — no framework dependencies
│   ├── models/
│   │   ├── checkout.py                  # Amount, PaymentRequest, SessionsRequest, etc.
│   │   └── terminal.py                  # DecodedTerminalResponse, PaymentSummaryField
│   └── ports/                           # Abstract interfaces (driven side)
│       ├── checkout_port.py             # CheckoutGateway ABC
│       ├── terminal_port.py             # TerminalGateway ABC
│       ├── management_port.py           # ManagementGateway ABC
│       └── validator_port.py            # PayloadValidator ABC
│
├── application/                         # USE CASES — orchestration
│   ├── checkout_service.py
│   ├── terminal_payment_service.py
│   ├── terminal_fleet_service.py
│   └── tools_service.py
│
├── infrastructure/                      # ADAPTERS — driven side (external)
│   ├── config.py                        # Env vars, Adyen client singleton
│   ├── adyen_checkout_adapter.py        # CheckoutGateway implementation
│   ├── adyen_terminal_adapter.py        # TerminalGateway implementation
│   ├── adyen_management_adapter.py      # ManagementGateway implementation
│   ├── adyen_validator_adapter.py       # PayloadValidator implementation
│   ├── terminal_decoder.py              # AdditionalResponse decoder
│   └── data/
│       └── verticals.py                 # Merchant vertical definitions
│
└── api/                                 # DRIVING ADAPTERS — HTTP layer
    ├── dependencies.py                  # FastAPI DI wiring
    ├── routers/
    │   ├── checkout.py                  # /api/checkout/*
    │   ├── terminal_payments.py         # /api/terminal/*
    │   ├── terminal_fleet.py            # /api/fleet/*
    │   ├── tools.py                     # /api/tools/*
    │   └── config.py                    # /api/config/*
    └── schemas/                         # Request/Response DTOs
        ├── checkout.py
        ├── terminal.py
        └── tools.py
```
