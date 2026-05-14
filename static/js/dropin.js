// dropin.js – Adyen Drop-in with native 3DS2
//
// Requires adyen_api.js to be loaded first (shared helpers).

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

      paymentMethodsConfiguration: {
        card: {
          hasHolderName: true,
          holderNameRequired: true,
          // billingAddressRequired: true
          billingAddressRequired: false,
          // Show "Save for my next payment" checkbox (tokenisation)
          enableStoreDetails: true,
        },
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
        // Show any stored (tokenised) payment methods for this shopper
        showStoredPaymentMethods: true,
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
