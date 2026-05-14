// adyen_api.js – Shared helpers for Adyen Drop-in and Card Component
//
// This file is loaded before dropin.js / card_component.js and provides the
// common API helpers and result-handling logic they both need.
//
// CHECKOUT_CONFIG is expected to be defined in a <script> block by the
// Flask template before this file is loaded.

// -------------------------------------------------------------------------
// Amount helper
// -------------------------------------------------------------------------
function getAmountMinorUnits() {
  return CHECKOUT_CONFIG.amountMinorUnits;
}

// -------------------------------------------------------------------------
// Generic fetch wrapper with error logging
// -------------------------------------------------------------------------
async function fetchApi(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    console.error(`[${url}]`, response.status, errorBody);
    throw new Error(errorBody?.error || `Request to ${url} failed`);
  }
  return response.json();
}

// -------------------------------------------------------------------------
// Fetch available payment methods from the server
// -------------------------------------------------------------------------
async function fetchPaymentMethods() {
  const params = new URLSearchParams({
    countryCode: CHECKOUT_CONFIG.countryCode,
    currency: CHECKOUT_CONFIG.currency,
  });
  const data = await fetchApi(`/api/paymentMethods?${params}`);
  return { paymentMethodsResponse: data.response, requestBody: data.requestBody };
}

// -------------------------------------------------------------------------
// Call the server's /payments endpoint
// -------------------------------------------------------------------------
async function callPayments(stateData) {
  return fetchApi("/api/payments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(stateData),
  });
}

// -------------------------------------------------------------------------
// Call the server's /payments/details endpoint
// -------------------------------------------------------------------------
async function callPaymentsDetails(stateData) {
  return fetchApi("/api/payments/details", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(stateData),
  });
}

// -------------------------------------------------------------------------
// handleServerResponse – routes the Adyen response to the correct action
// -------------------------------------------------------------------------
// Adyen's /payments and /payments/details responses can contain:
//   • resultCode  – final outcome (Authorised, Refused, etc.)
//   • action      – further action needed (3DS challenge, redirect, etc.)
async function handleServerResponse(response, component) {
  if (response.action) {
    component.handleAction(response.action);
  } else {
    await handleFinalResult(response.resultCode, response);
  }
}

// -------------------------------------------------------------------------
// handleFinalResult – redirect to a result page based on Adyen's resultCode
// -------------------------------------------------------------------------
async function handleFinalResult(resultCode, response) {
  // Adyen result codes: https://docs.adyen.com/development-resources/result-codes
  const status = ["Authorised", "Pending", "Received"].includes(resultCode)
    ? "success"
    : "failure";

  // POST the outcome to the server so it can be stored in the session.
  // The server returns a redirect URL, keeping the browser URL clean (/result).
  const res = await fetch("/result/store", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      status,
      resultCode,
      adyenResponse: status === "success" ? response : null,
    }),
  });
  const { redirect } = await res.json();
  window.location.href = redirect;
}
