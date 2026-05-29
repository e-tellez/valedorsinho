/**
 * TypeScript types matching the FastAPI Pydantic models and API responses.
 */

// ---------------------------------------------------------------------------
// Adyen config (from /api/config/client)
// ---------------------------------------------------------------------------

export interface ClientConfig {
  clientKey: string;
  environment: string;
  merchantAccount: string;
}

// ---------------------------------------------------------------------------
// Checkout
// ---------------------------------------------------------------------------

export interface Amount {
  value: number;
  currency: string;
}

export interface PaymentMethodsResponse {
  requestBody: Record<string, unknown>;
  response: {
    paymentMethods: Array<{
      name: string;
      type: string;
      brands?: string[];
    }>;
    storedPaymentMethods?: Array<{
      id: string;
      name: string;
      type: string;
      brand: string;
      lastFour: string;
      expiryMonth: string;
      expiryYear: string;
    }>;
  };
}

export interface CreatePaymentBody {
  paymentMethod: Record<string, unknown>;
  amountValue: number;
  currency: string;
  countryCode: string;
  shopperReference?: string;
  isGuest: boolean;
  shopperEmail?: string;
  browserInfo?: Record<string, unknown>;
  billingAddress?: Record<string, unknown>;
  storePaymentMethod?: boolean;
  returnUrl: string;
  origin: string;
}

export interface CreateSessionBody {
  amountValue: number;
  currency: string;
  countryCode: string;
  shopperReference?: string;
  isGuest: boolean;
  shopperEmail?: string;
  returnUrl: string;
}

export interface SessionsResponse {
  requestBody: Record<string, unknown>;
  response: {
    id: string;
    sessionData: string;
    [key: string]: unknown;
  };
}

export interface PaymentDetailsBody {
  details: Record<string, unknown>;
  paymentData?: string;
}

export interface RedirectBody {
  redirectResult: string;
  paymentData?: string;
}

export interface DisableStoredMethodBody {
  shopperReference: string;
  storedPaymentMethodId: string;
}

// ---------------------------------------------------------------------------
// Terminal Payments
// ---------------------------------------------------------------------------

export interface MerchantAccount {
  id: string;
  name: string;
}

export interface Store {
  id: string;
  reference: string;
  description: string;
  merchantId?: string;
  shopperStatement?: string;
  status?: string;
}

export interface Terminal {
  id: string;
  model: string;
  serialNumber: string;
  firmwareVersion?: string;
  assignment?: {
    companyId: string;
    merchantId: string;
    storeId?: string;
    status: string;
  };
}

export interface TerminalPaymentResult {
  success: boolean;
  resultTitle: string;
  resultMessage: string;
  decodedAdditionalResponse: Record<string, unknown> | string | null;
  paymentSummary: Array<{ label: string; value: string }>;
}

// ---------------------------------------------------------------------------
// Tools
// ---------------------------------------------------------------------------

export interface Vertical {
  key: string;
  label: string;
  description: string;
  payload: Record<string, unknown>;
}

export interface ValidationResult {
  valid: boolean;
  errors: Array<{
    field: string;
    error: string;
    rule: string;
  }>;
}

// ---------------------------------------------------------------------------
// Checkout flow state (held in React Context)
// ---------------------------------------------------------------------------

export interface CheckoutState {
  isGuest: boolean;
  shopperReference: string;
  amountMinorUnits: number;
  currency: string;
  countryCode: string;
  integrationType: string;
}
