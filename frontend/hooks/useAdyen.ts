"use client";

import { useEffect, useRef, useState } from "react";
import { useCheckoutConfig } from "./useCheckoutConfig";
import { ADYEN_SDK_VERSION } from "@/lib/constants";

/**
 * Load the Adyen Web SDK script and CSS, then return the global AdyenCheckout
 * constructor once both are ready.
 *
 * Usage:
 *   const { AdyenCheckout, ready, error } = useAdyen();
 */
export function useAdyen() {
  const { config, error: configError } = useCheckoutConfig();
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loadedRef = useRef(false);

  useEffect(() => {
    if (loadedRef.current || !config) return;
    loadedRef.current = true;

    const baseUrl = config.environment === "live"
      ? "https://checkoutshopper-live.adyen.com/checkoutshopper"
      : "https://checkoutshopper-test.adyen.com/checkoutshopper";

    // Load CSS
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = `${baseUrl}/sdk/${ADYEN_SDK_VERSION}/adyen.css`;
    document.head.appendChild(link);

    // Load JS
    const script = document.createElement("script");
    script.src = `${baseUrl}/sdk/${ADYEN_SDK_VERSION}/adyen.js`;
    script.async = true;
    script.onload = () => setReady(true);
    script.onerror = () => setError("Failed to load Adyen Web SDK");
    document.head.appendChild(script);
  }, [config]);

  return {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    AdyenCheckout: ready ? (window as any).AdyenCheckout : null,
    config,
    ready,
    error: error || configError,
  };
}
