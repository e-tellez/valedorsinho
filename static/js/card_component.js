// card_component.js – Adyen Card Component with native 3DS2
//
// Unlike the Drop-in (which renders a payment method selector + all forms),
// the Card Component renders only the card input fields.  The pay button and
// any surrounding UI are owned by this page, giving full control over layout.
//
// Requires adyen_api.js to be loaded first (shared helpers).

// Main initialisation
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
            "Pay " + CHECKOUT_CONFIG.currency + " " + (getAmountMinorUnits() / 100).toFixed(2);
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
        // Show "Save for my next payment" checkbox (tokenisation) – guests cannot store
        enableStoreDetails: !CHECKOUT_CONFIG.isGuest,
      })
      .mount("#card-container");

    document.getElementById("pm-request").innerHTML =
      syntaxHighlight(pmRequestBody);
    document.getElementById("pm-response").innerHTML =
      syntaxHighlight(paymentMethodsResponse);
    initPreviewCopyButtons();

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
