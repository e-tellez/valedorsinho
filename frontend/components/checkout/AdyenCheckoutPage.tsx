"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useCheckout } from "@/context/CheckoutContext";
import { useCheckoutConfig } from "@/hooks/useCheckoutConfig";
import { useAdyen } from "@/hooks/useAdyen";
import { apiGet, apiPost } from "@/lib/api";
import { ADYEN_SDK_VERSION } from "@/lib/constants";
import StepIndicator from "@/components/checkout/StepIndicator";
import PreviewCard from "@/components/shared/PreviewCard";
import BackButton from "@/components/shared/BackButton";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AdyenCheckoutPageProps {
  product: "dropin" | "components";
  flow: "Advanced" | "Sessions";
}

// ---------------------------------------------------------------------------
// Shared helpers (port of adyen_api.js)
// ---------------------------------------------------------------------------

function syntaxHighlight(json: unknown): string {
  let str = JSON.stringify(json, null, 2);
  str = str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return str.replace(
    /("(\\u[\da-fA-F]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\bnull\b)/g,
    (match) => {
      let cls = "json-number";
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
      return `<span class="${cls}">${match}</span>`;
    },
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function AdyenCheckoutPage({ product, flow }: AdyenCheckoutPageProps) {
  const router = useRouter();
  const { state } = useCheckout();
  const { config, loading: configLoading } = useCheckoutConfig();
  const { ready: adyenLoaded, error: sdkError } = useAdyen();

  const containerRef = useRef<HTMLDivElement>(null);
  const mountedRef = useRef(false);

  const [previewLeft, setPreviewLeft] = useState<{ title: string; html: string } | null>(null);
  const [previewRight, setPreviewRight] = useState<{ title: string; html: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const displayAmount = (state.amountMinorUnits / 100).toFixed(2);
  const isDropin = product === "dropin";
  const isAdvanced = flow === "Advanced";

  // -----------------------------------------------------------------------
  // handleFinalResult — redirect to result page
  // -----------------------------------------------------------------------
  function handleFinalResult(resultCode: string, response: Record<string, unknown>) {
    const status = ["Authorised", "Pending", "Received"].includes(resultCode)
      ? "success"
      : "failure";

    try {
      sessionStorage.setItem("adyen_result", JSON.stringify(response));
    } catch {}

    const params = new URLSearchParams({
      status,
      resultCode,
      pspReference: (response?.pspReference as string) || "",
      integrationType: state.integrationType,
    });
    router.push(`/checkout/result?${params.toString()}`);
  }

  // -----------------------------------------------------------------------
  // handleServerResponse
  // -----------------------------------------------------------------------
  function handleServerResponse(response: Record<string, unknown>, component: any) {
    if (response.action) {
      component.handleAction(response.action);
    } else {
      handleFinalResult(response.resultCode as string, response);
    }
  }

  // -----------------------------------------------------------------------
  // Mount Adyen SDK
  // -----------------------------------------------------------------------
  // Show SDK load error
  useEffect(() => {
    if (sdkError) setError(sdkError);
  }, [sdkError]);

  useEffect(() => {
    if (!adyenLoaded || configLoading || !config || mountedRef.current) return;
    if (!containerRef.current) return;

    mountedRef.current = true;

    const initCheckout = async () => {
      try {
        const AdyenCheckout = (window as any).AdyenCheckout;
        if (!AdyenCheckout) {
          setError("Adyen SDK not loaded.");
          return;
        }

        if (isAdvanced) {
          // --- ADVANCED FLOW ---
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

          setPreviewLeft({
            title: "/paymentMethods request body",
            html: syntaxHighlight(pmData.requestBody),
          });
          setPreviewRight({
            title: "/paymentMethods response",
            html: syntaxHighlight(pmData.response),
          });

          const checkoutConfig: any = {
            clientKey: config.clientKey,
            environment: config.environment,
            paymentMethodsResponse: pmData.response,
            locale: "en-US",
            analytics: { enabled: true },

            onSubmit: async (sdkState: any, component: any) => {
              if (isDropin) component.setStatus("loading");
              try {
                const result = await apiPost<any>("/api/checkout/payments", {
                  ...sdkState.data,
                  amountValue: state.amountMinorUnits,
                  currency: state.currency,
                  countryCode: state.countryCode,
                  shopperReference: state.shopperReference || undefined,
                  isGuest: state.isGuest,
                  returnUrl: `${window.location.origin}/checkout/result`,
                  origin: window.location.origin,
                });
                handleServerResponse(result, component);
              } catch (err: any) {
                console.error("onSubmit error:", err);
                if (isDropin) {
                  component.setStatus("error", { message: err.message || "Payment failed." });
                }
              }
            },

            onAdditionalDetails: async (sdkState: any, component: any) => {
              if (isDropin) component.setStatus("loading");
              try {
                const result = await apiPost<any>("/api/checkout/payments/details", sdkState.data);
                handleServerResponse(result, component);
              } catch (err: any) {
                console.error("onAdditionalDetails error:", err);
                if (isDropin) {
                  component.setStatus("error", { message: "Authentication failed." });
                }
              }
            },

            onError: (error: any) => console.error("Adyen error:", error),

            onPaymentCompleted: async (result: any) => {
              handleFinalResult(result.resultCode, result);
            },
          };

          // Add card config for dropin
          if (isDropin) {
            checkoutConfig.paymentMethodsConfiguration = {
              card: {
                hasHolderName: true,
                holderNameRequired: true,
                billingAddressRequired: false,
                enableStoreDetails: !state.isGuest,
              },
            };
          }

          const checkout = await AdyenCheckout(checkoutConfig);

          if (isDropin) {
            checkout
              .create("dropin", {
                showStoredPaymentMethods: !state.isGuest,
                openFirstPaymentMethod: true,
              })
              .mount(containerRef.current);
          } else {
            const cardComponent = checkout
              .create("card", {
                hasHolderName: true,
                holderNameRequired: true,
                billingAddressRequired: false,
                enableStoreDetails: !state.isGuest,
              })
              .mount(containerRef.current);

            // Wire external pay button
            const payButton = document.getElementById("pay-button");
            if (payButton) {
              payButton.addEventListener("click", () => cardComponent.submit());
            }
          }
        } else {
          // --- SESSIONS FLOW ---
          const sessionData = await apiPost<{ response: any; requestBody: any }>(
            "/api/checkout/sessions",
            {
              amountValue: state.amountMinorUnits,
              currency: state.currency,
              countryCode: state.countryCode,
              shopperReference: state.shopperReference || undefined,
              isGuest: state.isGuest,
              returnUrl: `${window.location.origin}/checkout/result`,
            },
          );

          setPreviewLeft({
            title: "/sessions request body",
            html: syntaxHighlight(sessionData.requestBody),
          });
          setPreviewRight({
            title: "/sessions response",
            html: syntaxHighlight(sessionData.response),
          });

          const checkoutConfig: any = {
            clientKey: config.clientKey,
            environment: config.environment,
            session: {
              id: sessionData.response.id,
              sessionData: sessionData.response.sessionData,
            },
            locale: "en-US",
            analytics: { enabled: true },

            onPaymentCompleted: async (result: any) => {
              handleFinalResult(result.resultCode, result);
            },

            onError: (error: any) => console.error("Adyen error:", error),
          };

          if (isDropin) {
            checkoutConfig.paymentMethodsConfiguration = {
              card: {
                hasHolderName: true,
                holderNameRequired: true,
                billingAddressRequired: false,
                enableStoreDetails: !state.isGuest,
              },
            };
          }

          const checkout = await AdyenCheckout(checkoutConfig);

          if (isDropin) {
            checkout
              .create("dropin", {
                showStoredPaymentMethods: !state.isGuest,
                openFirstPaymentMethod: true,
              })
              .mount(containerRef.current);
          } else {
            const cardComponent = checkout
              .create("card", {
                hasHolderName: true,
                holderNameRequired: true,
                billingAddressRequired: false,
                enableStoreDetails: !state.isGuest,
              })
              .mount(containerRef.current);

            const payButton = document.getElementById("pay-button");
            if (payButton) {
              payButton.addEventListener("click", () => cardComponent.submit());
            }
          }
        }
      } catch (err: any) {
        console.error("Checkout initialisation failed:", err);
        setError("Could not load payment form. Please refresh the page.");
      }
    };

    initCheckout();
  }, [adyenLoaded, configLoading, config]);

  // -----------------------------------------------------------------------
  // Render
  // -----------------------------------------------------------------------
  return (
    <div className="flex gap-6 items-start w-full max-w-[1200px]">
      {/* Main checkout panel */}
      <div className="bg-white rounded-lg shadow-md p-8 w-full max-w-[720px] shrink-0">
        <StepIndicator currentStep={4} />

        <div className="flex items-baseline justify-center gap-3 mb-4">
          <h1 className="text-xl font-bold text-gray-900 mb-0">Complete your order</h1>
          <div className="flex gap-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700">
              {isDropin ? "Drop-in" : "Components"}
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-50 text-green-700">
              {flow}
            </span>
          </div>
        </div>

        {/* Order summary */}
        <div className="bg-gray-50 border border-gray-200 rounded-md px-4 py-3 mb-6 text-sm text-gray-600">
          <strong className="text-gray-900">Order total:</strong> {state.currency} {displayAmount}
          <br />
          <strong className="text-gray-900">Shopper:</strong> {state.shopperReference || "Guest"}
        </div>

        {/* Adyen container */}
        {error ? (
          <p className="text-red-600 text-sm">{error}</p>
        ) : (
          <div ref={containerRef} className="min-h-[100px]" />
        )}

        {/* External pay button for Components */}
        {!isDropin && !error && (
          <button id="pay-button" className="btn-primary w-full max-w-[320px] mx-auto block !h-11 mt-4">
            Pay {state.currency} {displayAmount}
          </button>
        )}

        <BackButton href="/checkout/select-integration" label="Back" />
      </div>

      {/* API sidebar */}
      <div className="flex-1 min-w-0 flex flex-col gap-3 sticky top-10 max-h-[calc(100vh-80px)] overflow-y-auto">
        {previewLeft && (
          <PreviewCard title={previewLeft.title} contentId="preview-left" initialHtml={previewLeft.html} />
        )}
        {previewRight && (
          <PreviewCard title={previewRight.title} contentId="preview-right" initialHtml={previewRight.html} />
        )}
      </div>
    </div>
  );
}
