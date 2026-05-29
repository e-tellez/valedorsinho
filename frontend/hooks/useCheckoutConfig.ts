"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import type { ClientConfig } from "@/lib/types";

/**
 * Fetch the Adyen client-side config from the backend once on mount.
 * Returns { clientKey, environment, merchantAccount } or null while loading.
 */
export function useCheckoutConfig() {
  const [config, setConfig] = useState<ClientConfig | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<ClientConfig>("/api/config/client")
      .then(setConfig)
      .catch((error_) => setError(error_.message));
  }, []);

  const loading = config === null && error === null;
  return { config, error, loading };
}
