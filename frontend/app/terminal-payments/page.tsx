"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/api";
import BackButton from "@/components/shared/BackButton";

interface MerchantData {
  id: string;
  name?: string;
  companyId?: string;
}

interface StoreData {
  id: string;
  reference?: string;
  description?: string;
  shopperStatement?: string;
}

interface TerminalData {
  id: string;
  model?: string;
}

const FLOWS = [
  {
    href: "/terminal-payments/make-payment",
    title: "Make a Payment",
    desc: "Send a payment request to the terminal.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <rect x={1} y={4} width={22} height={16} rx={2} ry={2} />
        <line x1={1} y1={10} x2={23} y2={10} />
      </svg>
    ),
  },
  {
    href: "/terminal-payments/auth-capture",
    title: "Auth + Capture",
    desc: "Pre-authorize then capture in separate steps.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <path d="M9 12l2 2 4-4" />
      </svg>
    ),
  },
  {
    href: "/terminal-payments/card-acquisition",
    title: "Card Acquisition",
    desc: "Acquire card details without charging.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <rect x={2} y={5} width={20} height={14} rx={2} />
        <path d="M12 9v6" />
        <path d="M9 12h6" />
      </svg>
    ),
  },
  {
    href: "/terminal-payments/nfc",
    title: "NFC Flow",
    desc: "Identify, read, and write NFC tags on terminal.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <path d="M6 18.7V21a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-2.3" />
        <path d="M12 12a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" />
        <path d="M12 15c-4 0-6-2-6-5V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v7c0 3-2 5-6 5z" />
      </svg>
    ),
  },
];

export default function TerminalPaymentsPage() {
  const [companyAccount, setCompanyAccount] = useState("Loading\u2026");
  const [merchants, setMerchants] = useState<MerchantData[]>([]);
  const [stores, setStores] = useState<StoreData[]>([]);
  const [terminals, setTerminals] = useState<TerminalData[]>([]);

  const [selectedMerchant, setSelectedMerchant] = useState("");
  const [selectedStore, setSelectedStore] = useState("");
  const [selectedTerminal, setSelectedTerminal] = useState("");

  const [status, setStatus] = useState<{ msg: string; error: boolean } | null>(null);
  const [loadingMerchants, setLoadingMerchants] = useState(true);
  const [loadingStores, setLoadingStores] = useState(false);
  const [loadingTerminals, setLoadingTerminals] = useState(false);

  const flowsEnabled = !!selectedTerminal;

  // Fetch merchants on mount
  useEffect(() => {
    setLoadingMerchants(true);
    apiGet<{ data: MerchantData[] }>("/api/terminal/merchants")
      .then((res) => {
        const list = res.data || [];
        setMerchants(list);
        if (list.length > 0 && list[0].companyId) {
          setCompanyAccount(list[0].companyId);
        } else {
          setCompanyAccount("\u2014");
        }
        if (list.length === 1) {
          setSelectedMerchant(list[0].id);
        }
      })
      .catch((err) => {
        setStatus({ msg: "Failed to load merchants: " + err.message, error: true });
        setCompanyAccount("\u2014");
      })
      .finally(() => setLoadingMerchants(false));
  }, []);

  // Fetch stores + terminals when merchant changes
  useEffect(() => {
    if (!selectedMerchant) {
      setStores([]);
      setTerminals([]);
      setSelectedStore("");
      setSelectedTerminal("");
      return;
    }

    setLoadingStores(true);
    apiGet<{ data: StoreData[] }>(`/api/terminal/stores?merchantId=${encodeURIComponent(selectedMerchant)}`)
      .then((res) => setStores(res.data || []))
      .catch((err) => setStatus({ msg: "Failed to load stores: " + err.message, error: true }))
      .finally(() => setLoadingStores(false));

    fetchTerminals(selectedMerchant, "");
  }, [selectedMerchant]);

  // Re-fetch terminals when store changes
  useEffect(() => {
    if (!selectedMerchant) return;
    fetchTerminals(selectedMerchant, selectedStore);
  }, [selectedStore]);

  const fetchTerminals = useCallback((merchantId: string, storeId: string) => {
    setLoadingTerminals(true);
    setSelectedTerminal("");

    const params = new URLSearchParams({ merchantIds: merchantId, pageSize: "100" });
    if (storeId) params.set("storeIds", storeId);

    apiGet<{ data: TerminalData[] }>(`/api/terminal/terminals?${params.toString()}`)
      .then((res) => setTerminals(res.data || []))
      .catch((err) => setStatus({ msg: "Failed to load terminals: " + err.message, error: true }))
      .finally(() => setLoadingTerminals(false));
  }, []);

  function buildFlowHref(baseHref: string) {
    if (!selectedTerminal) return "#";
    return `${baseHref}?terminalId=${encodeURIComponent(selectedTerminal)}&merchantAccount=${encodeURIComponent(selectedMerchant)}`;
  }

  return (
    <div className="w-full max-w-[900px]">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Terminal Payments</h1>
        <p className="text-sm text-gray-500">Select a terminal to perform in-person payment flows.</p>
      </header>

      <div className="mb-5">
        <BackButton href="/" />
      </div>

      {/* Status */}
      {status && (
        <div className={`px-4 py-3 rounded-md text-sm mb-4 ${status.error ? "bg-red-50 text-red-700 border border-red-200" : "bg-blue-50 text-blue-700 border border-blue-200"}`}>
          {status.msg}
        </div>
      )}

      {/* Step 1 — Terminal selector */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-base font-bold text-gray-700 mb-4">1. Select Terminal</h2>
        <div className="grid grid-cols-2 gap-4">
          {/* Company account */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Company Account</label>
            <span className="block text-sm text-gray-800 font-medium">{companyAccount}</span>
          </div>

          {/* Merchant */}
          <div>
            <label htmlFor="merchant-select" className="block text-xs font-semibold text-gray-500 mb-1">Merchant Account</label>
            <select
              id="merchant-select"
              className="field-input"
              value={selectedMerchant}
              onChange={(e) => { setSelectedMerchant(e.target.value); setSelectedStore(""); setSelectedTerminal(""); setStatus(null); }}
              disabled={loadingMerchants || merchants.length === 0}
            >
              <option value="">{loadingMerchants ? "Loading\u2026" : merchants.length === 0 ? "No merchants found" : "Select merchant account\u2026"}</option>
              {merchants.map((m) => (
                <option key={m.id} value={m.id}>{m.name ? `${m.id} (${m.name})` : m.id}</option>
              ))}
            </select>
          </div>

          {/* Store */}
          <div>
            <label htmlFor="store-select" className="block text-xs font-semibold text-gray-500 mb-1">Store</label>
            <select
              id="store-select"
              className="field-input"
              value={selectedStore}
              onChange={(e) => { setSelectedStore(e.target.value); setSelectedTerminal(""); }}
              disabled={!selectedMerchant || loadingStores}
            >
              <option value="">{!selectedMerchant ? "Select a merchant first" : loadingStores ? "Loading\u2026" : "All stores"}</option>
              {stores.map((s) => (
                <option key={s.id} value={s.id} title={s.id}>{s.description || s.shopperStatement || s.reference || s.id}</option>
              ))}
            </select>
          </div>

          {/* Terminal */}
          <div>
            <label htmlFor="terminal-select" className="block text-xs font-semibold text-gray-500 mb-1">Terminal</label>
            <select
              id="terminal-select"
              className="field-input"
              value={selectedTerminal}
              onChange={(e) => { setSelectedTerminal(e.target.value); setStatus(null); }}
              disabled={!selectedMerchant || loadingTerminals}
            >
              <option value="">{!selectedMerchant ? "Select a merchant first" : loadingTerminals ? "Loading\u2026" : terminals.length === 0 ? "No terminals found" : "Select terminal\u2026"}</option>
              {terminals.map((t) => (
                <option key={t.id} value={t.id}>{t.model ? `${t.id} \u2013 ${t.model}` : t.id}</option>
              ))}
            </select>
          </div>
        </div>

        {selectedTerminal && (
          <div className="mt-3 text-sm text-green-700 font-medium">✓ Selected: {selectedTerminal}</div>
        )}
      </div>

      {/* Step 2 — Flow cards */}
      <div className={`${flowsEnabled ? "" : "opacity-50 pointer-events-none"}`}>
        <h2 className="text-base font-bold text-gray-700 mb-2">2. Choose Flow</h2>
        {!flowsEnabled && (
          <p className="text-sm text-gray-400 mb-3">Select a terminal above to unlock payment flows</p>
        )}

        <div className="grid grid-cols-2 gap-4">
          {FLOWS.map((flow) => (
            <Link
              key={flow.title}
              href={buildFlowHref(flow.href)}
              className="flex items-center gap-4 bg-white rounded-xl p-4 border border-gray-100 no-underline text-inherit transition-all duration-200 hover:shadow-md hover:-translate-y-0.5"
            >
              <div className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 bg-green-50 text-green-600">
                <div className="w-5 h-5">{flow.icon}</div>
              </div>
              <div className="flex-1 min-w-0">
                <span className="block text-[0.95rem] font-semibold text-gray-900">{flow.title}</span>
                <span className="block text-sm text-gray-500 leading-snug mt-0.5">{flow.desc}</span>
              </div>
              <span className="text-gray-300 text-xl font-light">&rsaquo;</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
