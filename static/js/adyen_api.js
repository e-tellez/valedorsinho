// adyen_api.js – Shared helpers for Adyen Drop-in and Card Component
//
// This file is loaded before dropin.js / card_component.js and provides the
// common API helpers and result-handling logic they both need.
//
// CHECKOUT_CONFIG is expected to be defined in a <script> block by the
// Flask template before this file is loaded.

// -------------------------------------------------------------------------
// JSON syntax highlighting (matches terminal_make_payment.js palette)
// -------------------------------------------------------------------------
function syntaxHighlight(json) {
  var str = JSON.stringify(json, null, 2);
  str = str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return str.replace(
    /("(\\u[\da-fA-F]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?|\bnull\b)/g,
    function (match) {
      var cls = "json-number";
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = "json-key";
          match = match.replace(/:$/, "") + ":";
        } else {
          cls = "json-string";
        }
      } else if (/true|false/.test(match)) {
        cls = "json-bool";
      } else if (/null/.test(match)) {
        cls = "json-null";
      }
      return '<span class="' + cls + '">' + match + "</span>";
    }
  );
}

// -------------------------------------------------------------------------
// Generic copy-button handler for .preview-copy-btn elements
// -------------------------------------------------------------------------
function initPreviewCopyButtons() {
  document.querySelectorAll(".preview-copy-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var targetId = btn.getAttribute("data-target");
      var pre = document.getElementById(targetId);
      if (!pre) return;
      navigator.clipboard.writeText(pre.textContent).then(function () {
        var orig = btn.textContent;
        btn.textContent = "Copied!";
        setTimeout(function () { btn.textContent = orig; }, 1500);
      });
    });
  });
}

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

  // Store the full Adyen response client-side.  sessionStorage is per-tab,
  // survives same-origin navigations, and has ~5 MB of space – unlike
  // cookies which are limited to ~4 KB.
  try {
    sessionStorage.setItem("adyen_result", JSON.stringify(response));
  } catch (e) {
    console.warn("Could not store Adyen response in sessionStorage:", e);
  }

  // POST only the small metadata to the server (fits in the session cookie).
  // The server returns a redirect URL, keeping the browser URL clean (/result).
  const res = await fetch("/result/store", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      status,
      resultCode,
      pspReference: response?.pspReference || null,
    }),
  });
  const { redirect } = await res.json();
  window.location.href = redirect;
}
