# Valedorsinho API Contract

> E-commerce and Adyen payment integration (Private)

**Base URL:** `https://<valedorsinho-service>.up.railway.app`

In development, the Next.js frontend rewrites `/api/*` → `http://localhost:8000/api/*` via `next.config.mjs`.

## Authentication

All endpoints require a valid JWT in the `Authorization: Bearer <token>` header.

---

## 1. Config

### GET /api/config/client

Return the client-side Adyen configuration needed to initialize the Drop-in SDK.

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

> **`requestBody` field:** All checkout responses include a `requestBody` key containing the raw Adyen API request sent by the backend. This is returned for debug display on the frontend only — it is not part of the Adyen response.

### GET /api/checkout/payment-methods

Fetch available payment methods for the current shopper. Used by the Advanced flow and the Manage Payments flow.

**Query Parameters:**

| Param            | Type   | Required | Default  | Description |
|------------------|--------|----------|----------|-------------|
| countryCode      | string | Yes      | `MX`     | ISO 3166-1 alpha-2 |
| shopperLocale    | string | No       | `en-US`  | BCP 47 locale for method display names |
| shopperReference | string | No       | —        | Shopper ID — include to also return stored methods |
| amountValue      | int    | No       | —        | Transaction amount in minor units |
| currency         | string | No       | —        | ISO 4217 (e.g. `MXN`) — required when `amountValue` is set |

> **Amount filtering:** `amountValue` and `currency` are optional. When omitted, Adyen returns the complete set of payment methods for the merchant/country (recommended — avoids filtering out methods like OXXO that have amount restrictions). Pass both only when you need Adyen to pre-filter against a known transaction value.

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

> `amountValue` is in **minor units** (e.g. `1000` = MXN 10.00). Omit `shopperReference` and `shopperEmail` for guest shoppers.

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

> When saving a card without charging (Manage Payments flow), set `amountValue: 0` and `storePaymentMethod: true`.

**Response `200`:**

```json
{
  "resultCode": "Authorised | Pending | Received | RedirectShopper | IdentifyShopper | ChallengeShopper | Error | Cancelled | Refused",
  "pspReference": "string",
  "action": {}
}
```

> `action` is present for 3DS / redirect flows — call `component.handleAction(action)` when it exists.

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

Resolve the result after a browser redirect (Advanced and Sessions flows).

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

Remove a stored payment method. Called by the Manage Payments Drop-in via `onDisableStoredPaymentMethod`.

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

Forward a Nexo `SaleToPOIRequest` to the target terminal (proxied to the Adyen Terminal API).

**Request Body:** Raw `SaleToPOIRequest` (Nexo Retailer protocol v3.0).

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

> `RequestedAmount` is in **major units** (e.g. `10.00` = MXN 10.00). `SaleToAcquirerData` and `TransactionConditions` are optional.

**Response `200`:** Raw `SaleToPOIResponse` (pass-through from terminal).

---

### POST /api/terminal/decode-response

Decode a raw `SaleToPOIResponse` into a structured display result.

**Request Body:** Raw `SaleToPOIResponse` as returned by `POST /api/terminal/make-payment`.

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

> `errors` is empty when `valid` is `true`.

---

### POST /api/tools/payload-suggested

Generate a suggested `/payments` payload for one or more merchant verticals.

**Request Body:**

```json
{
  "verticals": ["retail", "hotels"]
}
```

**Available vertical keys:** `minimum_mandatory`, `hotels`, `airlines`, `digital_wallet`, `subscription`, `ride_hailing`, `restaurants`, `retail`, `tickets`

> When multiple verticals are selected their fields are deep-merged. Unknown vertical keys return `400`.

**Response `200`:**

```json
{
  "payload": {
    "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
    "reference": "order-001",
    "amount": { "value": 1000, "currency": "EUR" },
    "paymentMethod": { "type": "scheme" },
    "returnUrl": "https://your-domain.com/redirect"
  }
}
```

---

## 6. Auth

### GET /api/auth/config

Return the active Adyen credentials for the authenticated user.

**Response `200`:**

```json
{
  "role": "admin | im | user",
  "api_key": "string",
  "client_key": "string",
  "merchant_account": "string",
  "environment": "test | live",
  "is_custom": true,
  "locked": false
}
```

---

### PUT /api/auth/config

Save personal Adyen credentials. Allowed for `admin` and `im` roles only.

**Request Body:**

```json
{
  "api_key": "string",
  "client_key": "string",
  "merchant_account": "string"
}
```

**Response `200`:** Same shape as `GET /api/auth/config`.

> Returns `403` if role is `user` or if the existing config has `locked: true`.

---

## 7. Webhooks

### POST /api/webhooks/{user_id}

Adyen notification listener. **Not called by the frontend** — Adyen calls this directly.

> Configure this URL in Adyen Customer Area → Developers → Webhooks using the user's profile `id` (Supabase `auth.users.id`) as `user_id`. Auth is currently handled by Supabase.

**Response `200`:** Always `{ "notificationResponse": "[accepted]" }`.

---

### GET /api/webhooks

Return the authenticated user's non-expired webhooks, ordered by `received_at` descending.

**Query Parameters:**

| Param  | Type   | Required | Description                      |
|--------|--------|----------|----------------------------------|
| limit  | number | No       | Max results 1–100 (default: 50)  |
| offset | number | No       | Pagination offset (default: 0)   |

**Response `200`:**

```json
{
  "items": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "merchant_account": "string",
      "event_code": "AUTHORISATION",
      "psp_reference": "string",
      "merchant_reference": "string",
      "amount_value": 1000,
      "amount_currency": "EUR",
      "success": true,
      "live": false,
      "received_at": "2025-01-01T00:00:00Z",
      "expires_at": "2025-01-04T00:00:00Z"
    }
  ]
}
```

> Retention: `admin` — 5 days; `im` / `user` — 3 days.

---

### GET /api/webhooks/{id}

Return a single webhook event including its full raw payload.

**Response `200`:** Same as a single item from `GET /api/webhooks`, plus:

```json
{
  "payload": {}
}
```

> Returns `404` if not found, expired, or belonging to a different user.

---

## Error Format

```json
{ "detail": "string" }
```

| Code | Meaning                          |
|------|----------------------------------|
| 200  | OK                               |
| 400  | Bad Request / validation error   |
| 401  | Unauthorized                     |
| 422  | Unprocessable Entity (FastAPI)   |
| 500  | Internal Server Error            |

---

## Notes

- **Amount units:** Online checkout uses **minor units** (`amountValue: 1000` = 10.00). Terminal payments use **major units** (`RequestedAmount: 10.00`).
- **Proxy:** `next.config.mjs` rewrites `/api/*` → `http://localhost:8000/api/*` in dev. In production, `VALEDORSINHO_API_URL` (set in Vercel, pointing to the Railway service) is used as the rewrite destination.
- **CORS:** Backend allows `http://localhost:3000` (dev) and `https://etellez.com` (prod).
