# Valedorsinho API Contract

> E-commerce and Adyen payment integration (Private)

## Base URL

```
https://<valedorsinho-service>.onrender.com
```

> All routes are prefixed with `/api`. In development, the Next.js frontend rewrites `/api/*` → `http://localhost:8000/api/*` via `next.config.mjs`.

## Authentication

All endpoints require a valid JWT in the `Authorization: Bearer <token>` header.

---

## 1. Config

### GET /api/config/client

Return the client-side Adyen configuration needed to initialize the SDK.

**Response `200`:**

```json
{
  "clientKey": "test_xxx",
  "environment": "test | live",
  "merchantAccount": "string"
}
```

---

## 2. Online Checkout

### GET /api/checkout/payment-methods

Fetch available payment methods for the current shopper context. Used by both Advanced and Manage Payments flows.

**Query Parameters:**

| Param            | Type   | Required | Description                          |
|------------------|--------|----------|--------------------------------------|
| countryCode      | string | Yes      | ISO 3166-1 alpha-2 (e.g. `MX`)      |
| currency         | string | Yes      | ISO 4217 (e.g. `MXN`)               |
| shopperReference | string | No       | Shopper ID — required to return stored methods |

**Response `200`:**

```json
{
  "requestBody": {},
  "response": {
    "paymentMethods": [
      { "name": "string", "type": "string", "brands": ["visa"] }
    ],
    "storedPaymentMethods": [
      {
        "id": "string",
        "name": "string",
        "type": "string",
        "brand": "string",
        "lastFour": "string",
        "expiryMonth": "string",
        "expiryYear": "string"
      }
    ]
  }
}
```

> `requestBody` is the raw Adyen API request — returned for debug display on the frontend.

---

### POST /api/checkout/sessions

Create an Adyen Sessions-flow session.

**Request Body:**

```json
{
  "amountValue": 1000,
  "currency": "MXN",
  "countryCode": "MX",
  "shopperReference": "shopper_123",
  "isGuest": false,
  "shopperEmail": "shopper@example.com",
  "returnUrl": "https://etellez.com/adyen/checkout/result"
}
```

> `amountValue` is in **minor units** (e.g. `1000` = MXN 10.00). `shopperReference` and `shopperEmail` are omitted for guest shoppers.

**Response `200`:**

```json
{
  "requestBody": {},
  "response": {
    "id": "CS_xxx",
    "sessionData": "string"
  }
}
```

---

### POST /api/checkout/payments

Create a payment — Advanced flow only.

**Request Body:**

```json
{
  "paymentMethod": {},
  "amountValue": 1000,
  "currency": "MXN",
  "countryCode": "MX",
  "shopperReference": "shopper_123",
  "isGuest": false,
  "shopperEmail": "shopper@example.com",
  "browserInfo": {},
  "billingAddress": {},
  "storePaymentMethod": false,
  "returnUrl": "https://etellez.com/adyen/checkout/result",
  "origin": "https://etellez.com"
}
```

> When saving a card without charging (Manage Payments flow), `amountValue` is `0` and `storePaymentMethod` is `true`.

**Response `200`:**

```json
{
  "resultCode": "Authorised | Pending | Received | RedirectShopper | IdentifyShopper | ChallengeShopper | Error | Cancelled | Refused",
  "pspReference": "string",
  "action": {}
}
```

> `action` is present for 3DS / redirect flows. The frontend calls `component.handleAction(action)` when it exists.

---

### POST /api/checkout/payments/details

Submit additional details for 3DS or redirect flows — Advanced flow only.

**Request Body:**

```json
{
  "details": {},
  "paymentData": "string"
}
```

**Response `200`:** Same shape as `POST /api/checkout/payments`.

---

### POST /api/checkout/redirect

Resolve the result after a browser redirect (both Advanced and Sessions flows).

**Request Body:**

```json
{
  "redirectResult": "string",
  "paymentData": "string"
}
```

**Response `200`:** Same shape as `POST /api/checkout/payments`.

---

### POST /api/checkout/disable

Remove a stored payment method for a shopper. Called by the Manage Payments Drop-in via `onDisableStoredPaymentMethod`.

**Request Body:**

```json
{
  "shopperReference": "shopper_123",
  "storedPaymentMethodId": "string"
}
```

**Response `200`:**

```json
{
  "response": "[detail-successfully-disabled]"
}
```

---

## 3. Terminal Payments

### GET /api/terminal/merchants

List merchant accounts under the company.

**Response `200`:**

```json
{
  "data": [
    { "id": "string", "name": "string", "companyId": "string" }
  ]
}
```

---

### GET /api/terminal/stores

List stores for a merchant account.

**Query Parameters:**

| Param      | Type   | Required | Description      |
|------------|--------|----------|------------------|
| merchantId | string | Yes      | Merchant account |

**Response `200`:**

```json
{
  "data": [
    {
      "id": "string",
      "reference": "string",
      "description": "string",
      "shopperStatement": "string"
    }
  ]
}
```

---

### GET /api/terminal/terminals

List terminals for a merchant, optionally filtered by store.

**Query Parameters:**

| Param       | Type   | Required | Description               |
|-------------|--------|----------|---------------------------|
| merchantIds | string | Yes      | Merchant account ID        |
| pageSize    | number | No       | Max results (default: 100) |
| storeIds    | string | No       | Filter by store ID         |

**Response `200`:**

```json
{
  "data": [
    { "id": "string", "model": "string" }
  ]
}
```

---

### POST /api/terminal/make-payment

Forward a Nexo `SaleToPOIRequest` to the target terminal. The backend proxies this to the Adyen Terminal API.

**Request Body:** Raw `SaleToPOIRequest` object (Nexo Retailer protocol v3.0).

```json
{
  "SaleToPOIRequest": {
    "MessageHeader": {
      "ProtocolVersion": "3.0",
      "MessageClass": "Service",
      "MessageCategory": "Payment",
      "MessageType": "Request",
      "ServiceID": "string",
      "SaleID": "Valedorsinho",
      "POIID": "P400Plus-123456789"
    },
    "PaymentRequest": {
      "SaleData": {
        "SaleTransactionID": {
          "TransactionID": "string",
          "TimeStamp": "2025-01-01T00:00:00.000Z"
        },
        "SaleToAcquirerData": "base64encodedJson"
      },
      "PaymentTransaction": {
        "AmountsReq": { "Currency": "MXN", "RequestedAmount": 10.00 },
        "TransactionConditions": { "ForceEntryMode": ["Contactless"] }
      },
      "PaymentData": { "PaymentType": "Normal" }
    }
  }
}
```

> `RequestedAmount` is in **major units** (e.g. `10.00` = MXN 10.00). `SaleToAcquirerData` is a base64-encoded JSON string. `TransactionConditions` and `SaleToAcquirerData` are optional.

**Response `200`:** Raw `SaleToPOIResponse` object from the terminal (pass-through).

---

### POST /api/terminal/decode-response

Decode a raw `SaleToPOIResponse` into a structured result for display.

**Request Body:** Raw `SaleToPOIResponse` object (as returned by `POST /api/terminal/make-payment`).

**Response `200`:**

```json
{
  "success": true,
  "resultTitle": "Payment Authorised",
  "resultMessage": "string",
  "decodedAdditionalResponse": {},
  "paymentSummary": [
    { "label": "string", "value": "string" }
  ]
}
```

---

## 4. Fleet Management

### GET /api/fleet/terminals

Paginated list of all terminals in the fleet (company-wide).

**Query Parameters:**

| Param       | Type   | Required | Description                  |
|-------------|--------|----------|------------------------------|
| pageNumber  | number | No       | Page number (default: 1)     |
| pageSize    | number | No       | Items per page (default: 20) |
| searchQuery | string | No       | Filter by serial number or terminal ID |

**Response `200`:**

```json
{
  "data": [
    {
      "id": "string",
      "model": "string",
      "serialNumber": "string",
      "firmwareVersion": "string",
      "lastActivityAt": "2025-01-01T00:00:00Z",
      "assignment": {
        "companyId": "string",
        "merchantId": "string",
        "storeId": "string",
        "status": "Boarded | Inventory | ReassignToMerchantInventory | ReassignToStore"
      }
    }
  ],
  "pagesTotal": 5
}
```

---

### GET /api/fleet/stores

List stores for a merchant (fleet context). Same shape as `GET /api/terminal/stores`.

**Query Parameters:**

| Param      | Type   | Required | Description      |
|------------|--------|----------|------------------|
| merchantId | string | Yes      | Merchant account |

**Response `200`:** Same shape as `GET /api/terminal/stores`.

---

### POST /api/fleet/reassign

Reassign one or more terminals to a different store.

**Request Body:**

```json
{
  "terminalIds": ["P400Plus-123456789"],
  "storeId": "string",
  "merchantId": "string"
}
```

**Response `200`:**

```json
{
  "summary": "Reassignment complete."
}
```

---

## 5. Tools

### POST /api/tools/validate-payload

Validate a `/payments` JSON payload against the Adyen OpenAPI spec.

**Request Body:**

```json
{
  "payload": {
    "merchantAccount": "string",
    "reference": "string",
    "amount": { "value": 1000, "currency": "EUR" },
    "paymentMethod": {},
    "returnUrl": "string"
  }
}
```

**Response `200`:**

```json
{
  "valid": true,
  "errors": [
    { "field": "string", "error": "string", "rule": "string" }
  ]
}
```

> `errors` is empty (or omitted) when `valid` is `true`.

---

## 6. E-Commerce (Planned)

> Not yet consumed by the frontend. Implement once the e-commerce layer is active.

### GET /api/products

### POST /api/orders

### GET /api/orders/{id}

---

## Error Format

FastAPI default error shape — the frontend `api.ts` reads `detail` first, then falls back to `error`:

```json
{
  "detail": "string"
}
```

**HTTP status codes used:**

| Code | Meaning                          |
|------|----------------------------------|
| 200  | OK                               |
| 201  | Created                          |
| 400  | Bad Request / validation error   |
| 401  | Unauthorized                     |
| 422  | Unprocessable Entity (FastAPI)   |
| 500  | Internal Server Error            |

---

## Environment Variables

### Backend (FastAPI — set in Render)

| Variable                  | Description                                              |
|---------------------------|----------------------------------------------------------|
| `ADYEN_API_KEY`           | Adyen API key (from Adyen Customer Area)                 |
| `ADYEN_MERCHANT_ACCOUNT`  | Adyen merchant account name                              |
| `ADYEN_CLIENT_KEY`        | Returned to frontend via `GET /api/config/client`        |
| `ADYEN_ENVIRONMENT`       | `test` or `live` — returned via `GET /api/config/client` |
| `ADYEN_HMAC_KEY`          | HMAC key for webhook signature validation                |
| `ADYEN_TERMINAL_API_URL`  | Adyen Terminal API base URL (cloud or local)             |
| `ALLOWED_ORIGIN`          | Frontend origin for CORS (`https://etellez.com`)         |
| `JWT_SECRET`              | Secret for validating JWTs issued by the auth service    |

### Frontend (Next.js — set in Vercel)

| Variable                  | Description                                              |
|---------------------------|----------------------------------------------------------|
| `VALEDORSINHO_API_URL`    | Render service base URL (used in production rewrites)    |

> **Never commit actual secrets.** Keep a `.env.example` with placeholder values in each repo.

---

## Notes

- **Amount units:** Online checkout uses **minor units** (`amountValue: 1000` = 10.00). Terminal payments use **major units** (`RequestedAmount: 10.00`).
- **Proxy:** `next.config.mjs` rewrites `/api/*` → `http://localhost:8000/api/*` in dev. In production, update the rewrite destination to `VALEDORSINHO_API_URL`.
- **CORS:** Backend must allow `http://localhost:3000` (dev) and `https://etellez.com` (prod).
- **Adyen webhook:** The backend should handle `POST /api/webhooks/adyen` for payment status updates. The frontend does not call this directly.
