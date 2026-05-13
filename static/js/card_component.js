// card_component.js – Adyen Card Component with native 3DS2
//
// Unlike the Drop-in (which renders a payment method selector + all forms),
// the Card Component renders only the card input fields.  The pay button and
// any surrounding UI are owned by this page, giving full control over layout.
//
// CHECKOUT_CONFIG is injected by the Flask template:
//   .clientKey        – Adyen client key
//   .environment      – "test" or "live"
//   .shopperReference – username from step 1
//   .amountMinorUnits – amount in cents from step 1

// -------------------------------------------------------------------------
// Amount helper
// -------------------------------------------------------------------------
function getAmountMinorUnits() {
  return CHECKOUT_CONFIG.amountMinorUnits;
}

// -------------------------------------------------------------------------
// API helpers
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

async function callPayments(stateData) {
  const response = await fetch("/api/payments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(stateData),
  });
  if (!response.ok) throw new Error("Payment request failed");
  return response.json();
}

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
// handleServerResponse – routes Adyen response to the correct next action
// -------------------------------------------------------------------------
async function handleServerResponse(response, cardComponent) {
  if (response.action) {
    // Let the Card Component handle 3DS2 fingerprint / challenge / redirect
    cardComponent.handleAction(response.action);
  } else {
    await handleFinalResult(response.resultCode, response);
  }
}

// -------------------------------------------------------------------------
// handleFinalResult – POST outcome to server, then navigate to result page
// -------------------------------------------------------------------------
async function handleFinalResult(resultCode, response) {
  const status = ["Authorised", "Pending", "Received"].includes(resultCode)
    ? "success"
    : "failure";

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

// -------------------------------------------------------------------------
// Main initialisation
// -------------------------------------------------------------------------
(async () => {
  try {
    const { paymentMethodsResponse, requestBody: pmRequestBody } = await fetchPaymentMethods();

    // Create the core AdyenCheckout session object
    const checkout = await AdyenCheckout({
      clientKey: CHECKOUT_CONFIG.clientKey,
      environment: CHECKOUT_CONFIG.environment,
      paymentMethodsResponse: paymentMethodsResponse,
      locale: "en-US",
      analytics: { enabled: true },

      // onSubmit fires when cardComponent.submit() is called (from the pay button)
      onSubmit: async (state, cardComponent) => {
        document.getElementById("pay-button").disabled = true;
        document.getElementById("pay-button").textContent = "Processing…";
        try {
          const result = await callPayments({
            ...state.data,
            amountMinorUnits: getAmountMinorUnits(),
            shopperReference: CHECKOUT_CONFIG.shopperReference,
          });
          await handleServerResponse(result, cardComponent);
        } catch (err) {
          console.error("onSubmit error:", err);
          document.getElementById("pay-button").disabled = false;
          document.getElementById("pay-button").textContent =
            "Pay $" + (getAmountMinorUnits() / 100).toFixed(2);
        }
      },

      // onAdditionalDetails fires after a 3DS2 fingerprint or challenge
      onAdditionalDetails: async (state, cardComponent) => {
        try {
          const result = await callPaymentsDetails(state.data);
          await handleServerResponse(result, cardComponent);
        } catch (err) {
          console.error("onAdditionalDetails error:", err);
        }
      },

      onError: (error, component) => {
        console.error("Adyen component error:", error.name, error.message, component);
      },

      // onPaymentCompleted fires when the Card Component finalises the payment
      // in-browser (e.g. after a native 3DS2 challenge completes)
      onPaymentCompleted: async (result, component) => {
        await handleFinalResult(result.resultCode, result);
      },
    });

    // -----------------------------------------------------------------------
    // Create and mount the Card Component
    // -----------------------------------------------------------------------
    // checkout.create("card") renders only the card input fields –
    // no payment method selector, no built-in pay button.
    const cardComponent = checkout
      .create("card", {
        hasHolderName: true,
        holderNameRequired: true,
        billingAddressRequired: false,
        // Show "Save for my next payment" checkbox (tokenisation)
        enableStoreDetails: true,
      })
      .mount("#card-container");

    document.getElementById("pm-request").textContent =
      JSON.stringify(pmRequestBody, null, 2);
    document.getElementById("pm-response").textContent =
      JSON.stringify(paymentMethodsResponse, null, 2);

    // Wire the external pay button to submit the Card Component
    document.getElementById("pay-button").addEventListener("click", () => {
      cardComponent.submit();
    });

  } catch (err) {
    console.error("Checkout initialisation failed:", err);
    document.getElementById("card-container").innerText =
      "Could not load payment form. Please refresh the page.";
  }
})();
