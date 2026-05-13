// checkout.js – Adyen Drop-in - with native 3DS2

// -------------------------------------------------------------------------
// Amount helper
// -------------------------------------------------------------------------
// The amount was collected in step 1 and is injected into CHECKOUT_CONFIG
// by the Flask template as an integer number of minor units (cents).
function getAmountMinorUnits() {
  return CHECKOUT_CONFIG.amountMinorUnits;
}

// -------------------------------------------------------------------------
// Step 1 – Fetch available payment methods from the server
// -------------------------------------------------------------------------
async function fetchPaymentMethods() {
  const params = new URLSearchParams({
    countryCode: CHECKOUT_CONFIG.countryCode,
    currency: CHECKOUT_CONFIG.currency,
  });
  const response = await fetch(`/api/paymentMethods?${params}`);
  if (!response.ok) throw new Error("Could not load payment methods");
  const data = await response.json();
  return { paymentMethodsResponse: data.response, requestBody: data.requestBody };
}

// -------------------------------------------------------------------------
// Step 2 – Call the server's /payments endpoint
// -------------------------------------------------------------------------
async function callPayments(stateData) {
  const response = await fetch("/api/payments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(stateData),
  });
  if (!response.ok) throw new Error("Payment request failed");
  return response.json();
}

// -------------------------------------------------------------------------
// Step 3 – Call the server's /payments/details endpoint
// -------------------------------------------------------------------------
async function callPaymentsDetails(stateData) {
  const response = await fetch("/api/payments/details", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(stateData),
  });
  if (!response.ok) throw new Error("Payment details request failed");
  return response.json();
}

// -------------------------------------------------------------------------
// handleServerResponse – routes the Adyen response to the correct action
// -------------------------------------------------------------------------
// Adyen's /payments and /payments/details responses can contain:
//   • resultCode  – final outcome (Authorised, Refused, etc.)
//   • action      – further action needed (3DS challenge, redirect, etc.)
async function handleServerResponse(response, dropin) {
  if (response.action) {
    // The `action` object instructs the Drop-in to:
    //   - render a native 3DS2 fingerprint iframe (type: "threeDS2Fingerprint")
    //   - render a native 3DS2 challenge iframe (type: "threeDS2Challenge")
    //   - redirect the shopper to the issuer ACS page  (type: "redirect")
    //   - display a QR code / voucher                   (type: "voucher")
    // The Drop-in handles all of these automatically.
    dropin.handleAction(response.action);
  } else {
    // No further action required – pass the full response so the result
    // page can display the pspReference and other fields.
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

// Main initialisation
(async () => {
  try {
    // Load available payment methods before creating the AdyenCheckout instance
    const { paymentMethodsResponse, requestBody: pmRequestBody } = await fetchPaymentMethods();

    const checkout = await AdyenCheckout({
      clientKey: CHECKOUT_CONFIG.clientKey,
      environment: CHECKOUT_CONFIG.environment,
      paymentMethodsResponse: paymentMethodsResponse,
      locale: "en-US",
      analytics: {
        enabled: true,
      },

      // onSubmit – called when the shopper clicks "Pay"
      onSubmit: async (state, dropin) => {
        dropin.setStatus("loading");
        try {
          const amountMinorUnits = getAmountMinorUnits();
          const result = await callPayments({
            ...state.data,
            amountMinorUnits,
            // Forward the shopper username collected in step 1
            shopperReference: CHECKOUT_CONFIG.shopperReference,
          });

          await handleServerResponse(result, dropin);
        } catch (err) {
          console.error("onSubmit error:", err);
          dropin.setStatus("error", { message: err.message || "Payment failed. Please try again." });
        }
      },

      // -----------------------------------------------------------------------
      // onAdditionalDetails – called after native 3DS fingerprint / challenge
      // -----------------------------------------------------------------------
      onAdditionalDetails: async (state, dropin) => {
        dropin.setStatus("loading");
        try {
          const result = await callPaymentsDetails(state.data);
          await handleServerResponse(result, dropin);
        } catch (err) {
          console.error("onAdditionalDetails error:", err);
          dropin.setStatus("error", { message: "Authentication failed. Please try again." });
        }
      },

      onError: (error, component) => {
        console.error("Adyen component error:", error.name, error.message, component);
      },

      onPaymentCompleted: async (result, component) => {
        console.info("Payment completed:", result);
        // Pass the full result so pspReference is available on the result page
        await handleFinalResult(result.resultCode, result);
      },
    });

    const dropin = checkout
      .create("dropin", {

        paymentMethodsConfiguration: {
          card: {
            hasHolderName: true,
            holderNameRequired: true,
            // billingAddressRequired: true
            billingAddressRequired: false,
          },
        },

        // openFirstPaymentMethod: false
        openFirstPaymentMethod: true,
      })
      .mount("#dropin-container");

    document.getElementById("pm-request").textContent =
      JSON.stringify(pmRequestBody, null, 2);
    document.getElementById("pm-response").textContent =
      JSON.stringify(paymentMethodsResponse, null, 2);

  } catch (err) {
    console.error("Checkout initialisation failed:", err);
    document.getElementById("dropin-container").innerText =
      "Could not load payment form. Please refresh the page.";
  }
})();
