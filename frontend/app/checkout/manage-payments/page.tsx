"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useCheckout } from "@/context/CheckoutContext";
import { useCheckoutConfig } from "@/hooks/useCheckoutConfig";
import { useAdyen } from "@/hooks/useAdyen";
import { apiGet, apiPost } from "@/lib/api";
import StepIndicator from "@/components/checkout/StepIndicator";
import PreviewCard from "@/components/shared/PreviewCard";
import BackButton from "@/components/shared/BackButton";

function syntaxHighlight(json: unknown): string {
  let str = JSON.stringify(json, null, 2);
  str = str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return str.replace(
    /("(\\u[\da-fA-F]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\bnull\b)/g,
    (match) => {
      let cls = "json-number";
      if (/^"/.test(match)) {
        cls = /:$/.test(match) ? "json-key" : "json-string";
        if (/:$/.test(match)) match = match.replace(/:$/, "") + ":";
      } else if (/true|false/.test(match)) {
        cls = "json-bool";
      } else if (/null/.test(match)) {
        cls = "json-null";
      }
      return `<span class="${cls}">${match}</span>`;
    },
  );
}

export default function ManagePaymentsPage() {
  const { state } = useCheckout();
  const { config, loading: configLoading } = useCheckoutConfig();
  const { ready: adyenLoaded, error: sdkError } = useAdyen();

  const dropinContainerRef = useRef<HTMLDivElement>(null);
  const mountedRef = useRef(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<{ msg: string; type: "success" | "error" } | null>(null);
  const [previewLeft, setPreviewLeft] = useState<{ title: string; html: string } | null>(null);
  const [previewRight, setPreviewRight] = useState<{ title: string; html: string } | null>(null);

  const showStatus = useCallback((msg: string, type: "success" | "error") => {
    setStatus({ msg, type });
    if (type === "success") {
      setTimeout(() => setStatus(null), 4000);
    }
  }, []);

  // SDK error
  useEffect(() => {
    if (sdkError) setError(sdkError);
  }, [sdkError]);

  // Mount single Adyen Drop-in (stored cards + new card)
  useEffect(() => {
    if (!adyenLoaded || configLoading || !config || mountedRef.current) return;
    if (!dropinContainerRef.current) return;

    mountedRef.current = true;

    const init = async () => {
      try {
        const AdyenCheckout = (window as any).AdyenCheckout;
        if (!AdyenCheckout) {
          setError("Adyen SDK not loaded.");
          return;
        }

        // Fetch payment methods
        const params = new URLSearchParams({
          countryCode: state.countryCode,
          currency: state.currency,
        });
        if (state.shopperReference) {
          params.set("shopperReference", state.shopperReference);
        }
        const pmData = await apiGet<{ response: any; requestBody: any }>(
          `/api/checkout/payment-methods?${params.toString()}`,
        );

        setPreviewLeft({ title: "/paymentMethods request body", html: syntaxHighlight(pmData.requestBody) });
        setPreviewRight({ title: "/paymentMethods response", html: syntaxHighlight(pmData.response) });

        const checkout = await AdyenCheckout({
          clientKey: config.clientKey,
          environment: config.environment,
          paymentMethodsResponse: pmData.response,
          locale: "en-US",
          translations: {
            "en-US": {
              payButton: "Save card",
            },
          },
          analytics: { enabled: true },
          paymentMethodsConfiguration: {
            storedCard: {
              hideCVC: true,
              showPayButton: false,
            },
            card: {
              hasHolderName: true,
              holderNameRequired: true,
              billingAddressRequired: false,
            },
          },
          onSubmit: async (sdkState: any, component: any) => {
            try {
              const result = await apiPost<any>("/api/checkout/payments", {
                ...sdkState.data,
                amountValue: 0,
                currency: state.currency,
                countryCode: state.countryCode,
                shopperReference: state.shopperReference || undefined,
                isGuest: false,
                storePaymentMethod: true,
                returnUrl: `${window.location.origin}/checkout/manage-payments`,
                origin: window.location.origin,
              });
              if (result.action) {
                component.handleAction(result.action);
              } else if (["Authorised", "Pending", "Received"].includes(result.resultCode)) {
                showStatus("Card saved successfully. Refreshing\u2026", "success");
                setTimeout(() => window.location.reload(), 1500);
              } else {
                showStatus("Card could not be saved: " + (result.resultCode || "Unknown error"), "error");
              }
            } catch {
              showStatus("Failed to save card. Please try again.", "error");
            }
          },
          onAdditionalDetails: async (sdkState: any, component: any) => {
            try {
              const result = await apiPost<any>("/api/checkout/payments/details", sdkState.data);
              if (result.action) {
                component.handleAction(result.action);
              } else if (["Authorised", "Pending", "Received"].includes(result.resultCode)) {
                showStatus("Card saved successfully. Refreshing\u2026", "success");
                setTimeout(() => window.location.reload(), 1500);
              } else {
                showStatus("Card could not be saved: " + (result.resultCode || "Unknown error"), "error");
              }
            } catch {
              showStatus("Authentication failed. Please try again.", "error");
            }
          },
          onError: (err: any) => console.error("Manage payments error:", err),
          onPaymentCompleted: (result: any) => {
            if (["Authorised", "Pending", "Received"].includes(result.resultCode)) {
              showStatus("Card saved successfully. Refreshing\u2026", "success");
              setTimeout(() => window.location.reload(), 1500);
            } else {
              showStatus("Card could not be saved: " + (result.resultCode || "Unknown error"), "error");
            }
          },
        });

        checkout
          .create("dropin", {
            showStoredPaymentMethods: true,
            showPaymentMethods: true,
            showRemovePaymentMethodButton: true,
            openFirstPaymentMethod: false,
            openFirstStoredPaymentMethod: false,
            onDisableStoredPaymentMethod: async (
              storedPaymentMethodId: string,
              resolve: () => void,
              reject: () => void,
            ) => {
              try {
                await apiPost("/api/checkout/disable", {
                  storedPaymentMethodId,
                  shopperReference: state.shopperReference,
                });
                resolve();
                showStatus("Card removed successfully.", "success");
              } catch {
                reject();
                showStatus("Could not remove card. Please try again.", "error");
              }
            },
          })
          .mount(dropinContainerRef.current);
      } catch (err: any) {
        console.error("Manage payments init failed:", err);
        setError("Could not load payment methods. Please refresh the page.");
      } finally {
        setLoading(false);
      }
    };

    init();
  }, [adyenLoaded, configLoading, config]);

  return (
    <div className="flex gap-6 items-start w-full max-w-[1200px]">
      {/* Main panel */}
      <div className="bg-white rounded-lg shadow-md p-8 w-full max-w-[720px] shrink-0">
        <StepIndicator currentStep={3} />

        <h1 className="text-xl font-bold text-gray-900 mb-2 text-center">Manage payment methods</h1>
        <p className="text-sm text-gray-500 mb-5 text-center">
          Remove stored cards or add a new one. Adding a card will perform a zero-auth verification.
        </p>

        {/* Status banner */}
        {status && (
          <div
            className={`mb-4 px-4 py-3 rounded-md text-sm font-medium ${
              status.type === "success"
                ? "bg-green-50 text-green-700 border border-green-200"
                : "bg-red-50 text-red-700 border border-red-200"
            }`}
          >
            {status.msg}
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-12 gap-3">
            <div className="w-8 h-8 border-3 border-gray-200 border-t-primary rounded-full animate-spin" />
            <p className="text-sm text-gray-400">Loading payment methods…</p>
          </div>
        )}

        {!loading && error ? (
          <p className="text-red-600 text-sm">{error}</p>
        ) : null}

        <div className={loading || error ? "hidden" : ""}>
          <div ref={dropinContainerRef} />
        </div>

        <BackButton href="/checkout/select-integration" label="Back" />
      </div>

      {/* API sidebar */}
      <div className="flex-1 min-w-0 flex flex-col gap-3 sticky top-10 max-h-[calc(100vh-80px)] overflow-y-auto">
        {previewLeft && (
          <PreviewCard title={previewLeft.title} contentId="pm-request" initialHtml={previewLeft.html} />
        )}
        {previewRight && (
          <PreviewCard title={previewRight.title} contentId="pm-response" initialHtml={previewRight.html} />
        )}
      </div>
    </div>
  );
}
