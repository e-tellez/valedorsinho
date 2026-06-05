# Valedorsinho API Contract

> Auto-generated from the FastAPI backend (hexagonal architecture).
> Base URL: `http://localhost:8000` (dev) — configure via `CORS_ORIGINS`.

---

## Health

### `GET /health`

**Response** `200`
```json
{ "status": "ok" }
```

---

## Config

### `GET /api/config/client`

Returns Adyen client-side configuration for SDK initialization.

**Response** `200`
```json
{
  "clientKey": "test_XXXX",
  "environment": "test",
  "merchantAccount": "YOUR_MERCHANT_ACCOUNT"
}
```

---

## Checkout

### `GET /api/checkout/payment-methods`

Retrieve available payment methods.

**Query Parameters**
| Param | Type | Default | Required |
|---|---|---|---|
| `amountValue` | `int` | `1000` | No |
| `currency` | `string` | `"MXN"` | No |
| `countryCode` | `string` | `"MX"` | No |
| `shopperLocale` | `string` | `"en-US"` | No |
| `shopperReference` | `string \| null` | `null` | No |

**Response** `200`
```json
{
  "requestBody": {
    "merchantAccount": "...",
    "amount": { "value": 1000, "currency": "MXN" },
    "countryCode": "MX",
    "shopperLocale": "en-US",
    "channel": "Web"
  },
  "response": {
    "paymentMethods": [ ... ]
  }
}
```

---

### `POST /api/checkout/payments`

Initiate a payment (Advanced flow).

**Request Body** `application/json`
```typescript
{
  paymentMethod: Record<string, any>;   // encrypted card data from Web SDK
  amountValue: number;                  // minor units (e.g. 1000 = $10.00)
  currency: string;                     // default "MXN"
  countryCode: string;                  // default "MX"
  returnUrl: string;                    // required — redirect-back URL
  origin: string;                       // required — page origin for 3DS
  shopperReference?: string | null;     // for tokenization
  isGuest?: boolean;                    // default false
  shopperEmail?: string;                // default "shopper@example.com"
  browserInfo?: Record<string, any>;    // from Web SDK
  billingAddress?: {
    street?: string;
    houseNumberOrName?: string;
    postalCode?: string;
    city?: string;
    stateOrProvince?: string;
    country?: string;
  } | null;
  storePaymentMethod?: boolean;         // default false
}
```

**Response** `200` — Raw Adyen `/payments` response
```json
{
  "resultCode": "Authorised" | "RedirectShopper" | "ChallengeShopper" | "Refused" | ...,
  "pspReference": "...",
  "action": { ... }
}
```

---

### `POST /api/checkout/payments/details`

Submit 3DS2 challenge details.

**Request Body** `application/json`
```typescript
{
  details: Record<string, any>;    // from onAdditionalDetails callback
  paymentData?: string | null;     // from previous action
}
```

**Response** `200` — Raw Adyen `/payments/details` response
```json
{
  "resultCode": "Authorised" | "Refused" | ...,
  "pspReference": "..."
}
```

---

### `POST /api/checkout/sessions`

Create a checkout session (Sessions flow).

**Request Body** `application/json`
```typescript
{
  amountValue: number;
  currency?: string;                 // default "MXN"
  countryCode?: string;              // default "MX"
  returnUrl: string;
  shopperReference?: string | null;
  isGuest?: boolean;                 // default false
  shopperEmail?: string;             // default "shopper@example.com"
}
```

**Response** `200`
```json
{
  "requestBody": { ... },
  "response": {
    "id": "session-id",
    "sessionData": "...",
    "sessionResult": "..."
  }
}
```

---

### `POST /api/checkout/disable`

Remove a stored (tokenised) payment method.

**Request Body** `application/json`
```typescript
{
  shopperReference: string;
  storedPaymentMethodId: string;
}
```

**Response** `200` — Raw Adyen recurring disable response
```json
{
  "response": "[detail-successfully-disabled]"
}
```

---

### `POST /api/checkout/redirect`

Handle redirect back from issuer ACS page.

**Request Body** `application/json`
```typescript
{
  redirectResult: string;          // from URL query param after redirect
  paymentData?: string | null;     // stored before redirect
}
```

**Response** `200` — Raw Adyen `/payments/details` response
```json
{
  "resultCode": "Authorised" | "Refused" | ...,
  "pspReference": "..."
}
```

---

## Terminal Payments

### `GET /api/terminal/merchants`

List merchant accounts for cascading terminal selector.

**Query Parameters**
| Param | Type | Default | Required |
|---|---|---|---|
| `pageNumber` | `int \| null` | `null` | No |
| `pageSize` | `string` | `"100"` | No |

**Response** `200` — Raw Adyen Management API response
```json
{
  "data": [ { "id": "...", "name": "..." } ],
  "itemsTotal": 5,
  "pagesTotal": 1
}
```

---

### `GET /api/terminal/stores`

List stores for a merchant.

**Query Parameters**
| Param | Type | Default | Required |
|---|---|---|---|
| `merchantId` | `string` | — | **Yes** |
| `pageNumber` | `int \| null` | `null` | No |
| `pageSize` | `string` | `"100"` | No |

**Response** `200` — Raw Adyen Management API response

---

### `GET /api/terminal/terminals`

List terminals filtered by merchant/store.

**Query Parameters**
| Param | Type | Default | Required |
|---|---|---|---|
| `searchQuery` | `string \| null` | `null` | No |
| `merchantIds` | `string \| null` | `null` | No |
| `storeIds` | `string \| null` | `null` | No |
| `pageNumber` | `int \| null` | `null` | No |
| `pageSize` | `string` | `"100"` | No |

**Response** `200` — Raw Adyen Management API response

---

### `POST /api/terminal/make-payment`

Send a payment to a terminal via Terminal API Cloud.

**Request Body** `application/json` — Full `SaleToPOIRequest` payload
```typescript
{
  SaleToPOIRequest: {
    MessageHeader: {
      ProtocolVersion: string;
      MessageClass: string;
      MessageCategory: string;
      MessageType: string;
      ServiceID: string;
      SaleID: string;
      POIID: string;
    };
    PaymentRequest: {
      SaleData: {
        SaleTransactionID: { TransactionID: string; TimeStamp: string };
        SaleToAcquirerData: string;  // Base64-encoded JSON
      };
      PaymentTransaction: {
        AmountsReq: { Currency: string; RequestedAmount: number };
      };
    };
  };
}
```

**Response** `200` — Full `SaleToPOIResponse` from terminal
```json
{
  "SaleToPOIResponse": {
    "MessageHeader": { ... },
    "PaymentResponse": {
      "Response": { "Result": "Success" | "Failure", "ErrorCondition": "..." },
      "PaymentResult": { ... },
      "POIData": { ... }
    }
  }
}
```

---

### `POST /api/terminal/decode-response`

Decode a terminal response and extract payment summary.

**Request Body** `application/json` — Full `SaleToPOIResponse`

**Response** `200`
```typescript
{
  success: boolean;
  resultTitle: string;               // "Payment Approved" | "Payment Declined" | "Error"
  resultMessage: string;             // empty or "ErrorCondition: ..."
  decodedAdditionalResponse: Record<string, any> | string | null;
  paymentSummary: Array<{
    label: string;                   // "PSP Reference", "Card BIN", etc.
    value: string;
  }>;
}
```

---

## Terminal Fleet

### `GET /api/fleet/terminals`

List terminals with full filtering (fleet management view).

**Query Parameters**
| Param | Type | Default | Required |
|---|---|---|---|
| `searchQuery` | `string \| null` | `null` | No |
| `merchantIds` | `string \| null` | `null` | No |
| `storeIds` | `string \| null` | `null` | No |
| `countries` | `string \| null` | `null` | No |
| `brandModels` | `string \| null` | `null` | No |
| `pageNumber` | `int \| null` | `null` | No |
| `pageSize` | `string \| null` | `null` | No |

**Response** `200` — Raw Adyen Management API response

---

### `GET /api/fleet/stores`

List stores for a merchant (fleet context).

**Query Parameters**
| Param | Type | Default | Required |
|---|---|---|---|
| `merchantId` | `string` | — | **Yes** |
| `pageNumber` | `int \| null` | `null` | No |
| `pageSize` | `string` | `"100"` | No |

**Response** `200` — Raw Adyen Management API response

---

### `POST /api/fleet/reassign`

Reassign terminals to a different store.

**Request Body** `application/json`
```typescript
{
  terminalIds: string[];    // at least one
  storeId: string;
  merchantId: string;
}
```

**Response** `200`
```json
{
  "results": [
    { "terminalId": "V400m-123456789", "success": true },
    { "terminalId": "V400m-987654321", "success": false, "error": "..." }
  ],
  "summary": "1/2 terminals reassigned successfully"
}
```

---

## Tools

### `POST /api/tools/validate-payload`

Validate a `/payments` payload against the Adyen OpenAPI spec.

**Request Body** `application/json`
```typescript
{
  payload: Record<string, any>;   // raw /payments request object
}
```

**Response** `200`
```json
{
  "valid": true,
  "errors": []
}
```

**Error shape** (when `valid: false`)
```json
{
  "valid": false,
  "errors": [
    {
      "field": "amount.value",
      "error": "'value' is a required property",
      "rule": "required field"
    }
  ]
}
```

---

### `GET /api/tools/verticals`

Return merchant verticals with suggested payloads.

**Response** `200`
```typescript
Array<{
  key: string;           // e.g. "retail", "hospitality"
  label: string;         // display name
  description: string;
  payload: Record<string, any>;  // suggested /payments body
}>
```

---

## Error Format

All error responses use standard HTTP status codes with:
```json
{
  "detail": "Human-readable error message"
}
```

Common status codes:
- `400` — Bad request / validation error
- `401` / `403` — Adyen API key issues (proxied)
- `422` — Pydantic validation failure (auto from FastAPI)
- `500` — Internal server error
- `502` — Terminal API unreachable or invalid response
