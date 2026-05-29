"use client";

import { createContext, useContext, useState, useCallback, useEffect } from "react";
import type { CheckoutState } from "@/lib/types";
import { COUNTRY_CURRENCY_MAP } from "@/lib/constants";

const DEFAULT_STATE: CheckoutState = {
  isGuest: true,
  shopperReference: "",
  amountMinorUnits: 1000,
  currency: "MXN",
  countryCode: "MX",
  integrationType: "",
};

interface CheckoutContextValue {
  state: CheckoutState;
  setFlow: (isGuest: boolean, shopperReference?: string) => void;
  setOrder: (amountMinorUnits: number, countryCode: string) => void;
  setIntegration: (integrationType: string) => void;
  reset: () => void;
}

const STORAGE_KEY = "valedorsinho_checkout";

const Ctx = createContext<CheckoutContextValue | null>(null);

function persist(next: CheckoutState) {
  try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch {}
}

export function CheckoutProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<CheckoutState>(DEFAULT_STATE);

  // Restore from sessionStorage after hydration (client-only)
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (raw) setState({ ...DEFAULT_STATE, ...JSON.parse(raw) });
    } catch {}
  }, []);

  const setFlow = useCallback((isGuest: boolean, shopperReference?: string) => {
    setState((prev) => {
      const next = { ...prev, isGuest, shopperReference: isGuest ? "" : shopperReference ?? "" };
      persist(next);
      return next;
    });
  }, []);

  const setOrder = useCallback((amountMinorUnits: number, countryCode: string) => {
    setState((prev) => {
      const next = { ...prev, amountMinorUnits, countryCode, currency: COUNTRY_CURRENCY_MAP[countryCode] ?? "MXN" };
      persist(next);
      return next;
    });
  }, []);

  const setIntegration = useCallback((integrationType: string) => {
    setState((prev) => {
      const next = { ...prev, integrationType };
      persist(next);
      return next;
    });
  }, []);

  const reset = useCallback(() => {
    sessionStorage.removeItem(STORAGE_KEY);
    setState(DEFAULT_STATE);
  }, []);

  return (
    <Ctx.Provider value={{ state, setFlow, setOrder, setIntegration, reset }}>
      {children}
    </Ctx.Provider>
  );
}

export function useCheckout() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useCheckout must be used within <CheckoutProvider>");
  return ctx;
}
