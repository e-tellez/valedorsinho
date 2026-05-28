// sessions_dropin.js – Adyen Drop-in with /sessions flow
//
// Unlike the Advanced flow (dropin.js) which calls /paymentMethods, /payments,
// and /payments/details separately, the Sessions flow creates a single session
// and the Adyen Web SDK handles the entire payment lifecycle on the client side.
//
// Requires adyen_api.js to be loaded first (shared helpers).

// Main initialisation
(async () => {
  try {
    // Create a session on the server via POST /api/sessions
    const { response: sessionResponse, requestBody } = await fetchApi("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });

    const checkout = await AdyenCheckout({
      clientKey: CHECKOUT_CONFIG.clientKey,
      environment: CHECKOUT_CONFIG.environment,
      session: {
        id: sessionResponse.id,
        sessionData: sessionResponse.sessionData,
      },
      locale: "en-US",
      analytics: {
        enabled: true,
      },

      paymentMethodsConfiguration: {
        card: {
          hasHolderName: true,
          holderNameRequired: true,
          billingAddressRequired: false,
          // Show "Save for my next payment" checkbox (tokenisation) – guests cannot store
          enableStoreDetails: !CHECKOUT_CONFIG.isGuest,
        },
      },

      onPaymentCompleted: async (result, component) => {
        console.info("Payment completed:", result);
        await handleFinalResult(result.resultCode, result);
      },

      onError: (error, component) => {
        console.error("Adyen component error:", error.name, error.message, component);
      },
    });

    const dropin = checkout
      .create("dropin", {
        showStoredPaymentMethods: !CHECKOUT_CONFIG.isGuest,
        openFirstPaymentMethod: true,
      })
      .mount("#dropin-container");

    document.getElementById("session-request").innerHTML =
      syntaxHighlight(requestBody);
    document.getElementById("session-response").innerHTML =
      syntaxHighlight(sessionResponse);
    initPreviewCopyButtons();

  } catch (err) {
    console.error("Checkout initialisation failed:", err);
    document.getElementById("dropin-container").innerText =
      "Could not load payment form. Please refresh the page.";
  }
})();
