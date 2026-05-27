// manage_payments.js – Stored card management + add new card via zero-auth
//
// Uses two Adyen components on the same page:
//   1. Drop-in  – stored payment methods only (remove button, no pay button, no new PM)
//   2. Card Component – add a new card via zero-auth tokenisation
//
// Requires adyen_api.js to be loaded first.

// Helper to show a status banner
function showStatus(message, type) {
  const banner = document.getElementById("manage-status");
  banner.textContent = message;
  banner.className = "manage-status manage-status-" + type;
  banner.style.display = "block";
  if (type === "success") {
    setTimeout(() => { banner.style.display = "none"; }, 4000);
  }
}

// Main initialisation
(async () => {
  try {
    const { paymentMethodsResponse, requestBody: pmRequestBody } = await fetchPaymentMethods();

    // Show "no saved cards" message if there are none
    const hasStoredCards =
      paymentMethodsResponse.storedPaymentMethods &&
      paymentMethodsResponse.storedPaymentMethods.length > 0;

    // -----------------------------------------------------------------------
    // 1. Drop-in – stored cards only (view + remove)
    // -----------------------------------------------------------------------
    if (hasStoredCards) {
      const storedCheckout = await AdyenCheckout({
        clientKey: CHECKOUT_CONFIG.clientKey,
        environment: CHECKOUT_CONFIG.environment,
        paymentMethodsResponse: paymentMethodsResponse,
        locale: "en-US",
        analytics: { enabled: true },

        // These callbacks are required but the pay button is disabled,
        // so they should never fire for stored cards.
        onSubmit: () => {},
        onAdditionalDetails: () => {},
        onError: (error, component) => {
          console.error("Stored cards error:", error.name, error.message, component);
        },
      });

      storedCheckout
        .create("dropin", {
          showStoredPaymentMethods: true,
          showPaymentMethods: false,
          showPayButton: false,
          showRemovePaymentMethodButton: true,
          openFirstPaymentMethod: false,
          openFirstStoredPaymentMethod: false,

          onDisableStoredPaymentMethod: async (storedPaymentMethodId, resolve, reject) => {
            try {
              await fetchApi("/api/disable", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ storedPaymentMethodId }),
              });
              resolve();
              showStatus("Card removed successfully.", "success");
            } catch (err) {
              console.error("Disable error:", err);
              reject();
              showStatus("Could not remove card. Please try again.", "error");
            }
          },
        })
        .mount("#dropin-container");
    } else {
      document.getElementById("no-stored-cards").style.display = "block";
    }

    // -----------------------------------------------------------------------
    // 2. Card Component – add a new card (zero-auth tokenisation)
    // -----------------------------------------------------------------------
    const cardCheckout = await AdyenCheckout({
      clientKey: CHECKOUT_CONFIG.clientKey,
      environment: CHECKOUT_CONFIG.environment,
      paymentMethodsResponse: paymentMethodsResponse,
      locale: "en-US",
      analytics: { enabled: true },

      onSubmit: async (state, cardComponent) => {
        document.getElementById("save-card-button").disabled = true;
        document.getElementById("save-card-button").textContent = "Saving…";
        try {
          const result = await callPayments({
            ...state.data,
            amountMinorUnits: 0,
            shopperReference: CHECKOUT_CONFIG.shopperReference,
            storePaymentMethod: true,
          });

          if (result.action) {
            cardComponent.handleAction(result.action);
          } else if (["Authorised", "Pending", "Received"].includes(result.resultCode)) {
            showStatus("Card saved successfully. Refreshing…", "success");
            setTimeout(() => { window.location.reload(); }, 1500);
          } else {
            showStatus("Card could not be saved: " + (result.resultCode || "Unknown error"), "error");
            document.getElementById("save-card-button").disabled = false;
            document.getElementById("save-card-button").textContent = "Save card";
          }
        } catch (err) {
          console.error("onSubmit error:", err);
          showStatus("Failed to save card. Please try again.", "error");
          document.getElementById("save-card-button").disabled = false;
          document.getElementById("save-card-button").textContent = "Save card";
        }
      },

      onAdditionalDetails: async (state, cardComponent) => {
        try {
          const result = await callPaymentsDetails(state.data);
          if (result.action) {
            cardComponent.handleAction(result.action);
          } else if (["Authorised", "Pending", "Received"].includes(result.resultCode)) {
            showStatus("Card saved successfully. Refreshing…", "success");
            setTimeout(() => { window.location.reload(); }, 1500);
          } else {
            showStatus("Card could not be saved: " + (result.resultCode || "Unknown error"), "error");
            document.getElementById("save-card-button").disabled = false;
            document.getElementById("save-card-button").textContent = "Save card";
          }
        } catch (err) {
          console.error("onAdditionalDetails error:", err);
          showStatus("Authentication failed. Please try again.", "error");
          document.getElementById("save-card-button").disabled = false;
          document.getElementById("save-card-button").textContent = "Save card";
        }
      },

      onError: (error, component) => {
        console.error("Card component error:", error.name, error.message, component);
      },

      onPaymentCompleted: async (result, component) => {
        if (["Authorised", "Pending", "Received"].includes(result.resultCode)) {
          showStatus("Card saved successfully. Refreshing…", "success");
          setTimeout(() => { window.location.reload(); }, 1500);
        } else {
          showStatus("Card could not be saved: " + (result.resultCode || "Unknown error"), "error");
        }
      },
    });

    const cardComponent = cardCheckout
      .create("card", {
        hasHolderName: true,
        holderNameRequired: true,
        billingAddressRequired: false,
      })
      .mount("#card-container");

    // Wire the external "Save card" button
    document.getElementById("save-card-button").addEventListener("click", () => {
      cardComponent.submit();
    });

    // -----------------------------------------------------------------------
    // Sidebar debug info
    // -----------------------------------------------------------------------
    document.getElementById("pm-request").textContent =
      JSON.stringify(pmRequestBody, null, 2);
    document.getElementById("pm-response").textContent =
      JSON.stringify(paymentMethodsResponse, null, 2);

  } catch (err) {
    console.error("Manage payments initialisation failed:", err);
    document.getElementById("dropin-container").innerText =
      "Could not load payment methods. Please refresh the page.";
  }
})();
