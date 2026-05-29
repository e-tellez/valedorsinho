"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiGet, apiPost } from "@/lib/api";
import BackButton from "@/components/shared/BackButton";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const CURRENCIES = [
  "EUR", "USD", "GBP", "MXN", "BRL", "AUD", "CAD", "CHF",
  "SEK", "NOK", "DKK", "PLN", "CZK", "HUF", "SGD", "HKD",
  "NZD", "JPY", "ZAR", "AED", "SAR",
];

const FORCE_ENTRY_MODES = ["", "Contactless", "ICC", "MagStripe", "Manual", "RFID"];
const FORCE_ENTRY_LABELS: Record<string, string> = { "": "None" };

interface StoreOption { reference?: string; description?: string; }

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function generateServiceId() {
  return String(Math.floor(Math.random() * 10000000000));
}

function generateTransactionId() {
  return "ipp-" + Date.now().toString(36) + Math.random().toString(36).substring(2, 6);
}

function syntaxHighlight(json: unknown): string {
  let str = JSON.stringify(json, null, 2);
  str = str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return str.replace(
    /("(\\u[\da-fA-F]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\bnull\b)/g,
    (match) => {
      let cls = "json-number";
      if (/^"/.test(match)) {
        if (/:$/.test(match)) { cls = "json-key"; match = match.replace(/:$/, "") + ":"; }
        else { cls = "json-string"; }
      } else if (/true|false/.test(match)) { cls = "json-bool"; }
      else if (/null/.test(match)) { cls = "json-null"; }
      return `<span class="${cls}">${match}</span>`;
    },
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function MakePaymentPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const terminalId = searchParams.get("terminalId") || "";
  const merchantAccount = searchParams.get("merchantAccount") || "";

  // Form state
  const [amount, setAmount] = useState("10.00");
  const [currency, setCurrency] = useState("MXN");
  const [askGratuity, setAskGratuity] = useState(false);
  const [receiptHandler, setReceiptHandler] = useState(false);
  const [forceEntry, setForceEntry] = useState("");
  const [shopperRef, setShopperRef] = useState("");
  const [recurringContract, setRecurringContract] = useState("");
  const [authType, setAuthType] = useState("");
  const [shopperEmail, setShopperEmail] = useState("");
  const [store, setStore] = useState("");
  const [metadata, setMetadata] = useState<{ key: string; value: string }[]>([]);
  const [storeOptions, setStoreOptions] = useState<StoreOption[]>([]);
  const [sending, setSending] = useState(false);
  const [copied, setCopied] = useState(false);

  // Generated once
  const [serviceId] = useState(generateServiceId);
  const [transactionId] = useState(generateTransactionId);

  // Load stores
  useEffect(() => {
    if (!merchantAccount) return;
    apiGet<{ data: StoreOption[] }>(`/api/terminal/stores?merchantId=${encodeURIComponent(merchantAccount)}`)
      .then((res) => setStoreOptions(res.data || []))
      .catch(() => {});
  }, [merchantAccount]);

  // Build payload
  const { payload, acquirerData } = useMemo(() => {
    const parsedAmount = parseFloat(amount) || 0;

    // SaleToAcquirerData
    const acq: Record<string, unknown> = {};
    const tenderOpts: string[] = [];
    if (askGratuity) tenderOpts.push("AskGratuity");
    if (receiptHandler) tenderOpts.push("ReceiptHandler");
    if (tenderOpts.length) acq.tenderOption = tenderOpts.join(",");
    if (shopperRef.trim()) acq.shopperReference = shopperRef.trim();
    if (recurringContract) acq.recurringContract = recurringContract;
    if (authType) acq.authorisationType = authType;
    if (shopperEmail.trim() && shopperEmail.includes("@")) acq.shopperEmail = shopperEmail.trim();
    if (store) acq.store = store;
    const metaObj: Record<string, string> = {};
    metadata.forEach((m) => { if (m.key.trim()) metaObj[m.key.trim()] = m.value.trim(); });
    if (Object.keys(metaObj).length) acq.metadata = metaObj;

    const hasAcq = Object.keys(acq).length > 0;
    const acqB64 = hasAcq ? btoa(JSON.stringify(acq)) : null;

    const p: Record<string, unknown> = {
      SaleToPOIRequest: {
        MessageHeader: {
          ProtocolVersion: "3.0",
          MessageClass: "Service",
          MessageCategory: "Payment",
          MessageType: "Request",
          ServiceID: serviceId,
          SaleID: "Valedorsinho",
          POIID: terminalId || "<terminalId>",
        },
        PaymentRequest: {
          SaleData: {
            SaleTransactionID: { TransactionID: transactionId, TimeStamp: new Date().toISOString() },
            ...(acqB64 ? { SaleToAcquirerData: acqB64 } : {}),
          },
          PaymentTransaction: {
            AmountsReq: { Currency: currency, RequestedAmount: parsedAmount },
            ...(forceEntry ? { TransactionConditions: { ForceEntryMode: [forceEntry] } } : {}),
          },
          PaymentData: { PaymentType: "Normal" },
        },
      },
    };

    return { payload: p, acquirerData: hasAcq ? acq : null };
  }, [amount, currency, askGratuity, receiptHandler, forceEntry, shopperRef, recurringContract, authType, shopperEmail, store, metadata, serviceId, transactionId, terminalId]);

  const emailValid = !shopperEmail.trim() || shopperEmail.includes("@");
  const formValid = !!terminalId && (parseFloat(amount) > 0) && emailValid;

  async function handleSend() {
    setSending(true);
    try {
      const rawResponse = await apiPost<Record<string, unknown>>("/api/terminal/make-payment", payload);
      // Decode the response server-side to extract success, summary, etc.
      const decoded = await apiPost<Record<string, unknown>>("/api/terminal/decode-response", rawResponse);
      // Include the raw response for the Full Response card
      const result = { ...decoded, responseJson: rawResponse };
      sessionStorage.setItem("terminal_payment_result", JSON.stringify(result));
      const params = new URLSearchParams({
        terminalId,
        merchantAccount,
      });
      router.push(`/terminal-payments/result?${params.toString()}`);
    } catch (err: any) {
      alert("Request failed: " + (err.message || "Unknown error"));
      setSending(false);
    }
  }

  function handleCopy() {
    navigator.clipboard.writeText(JSON.stringify(payload, null, 2)).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  return (
    <div className="w-full max-w-[1100px]">
      <header className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900">Make a Payment</h1>
        <p className="text-sm text-gray-500">Configure and send a payment request to a terminal.</p>
      </header>

      {/* Top bar */}
      <div className="grid grid-cols-2 gap-6 items-center mb-5">
        <BackButton href="/terminal-payments" />
        <div className="flex items-center gap-3 bg-gray-50 border border-gray-200 rounded-md px-3.5 py-2 text-xs">
          <span className="text-gray-400 font-semibold">Terminal:</span>
          <span className="text-gray-800 font-medium">{terminalId || "\u2014"}</span>
          <span className="text-gray-400 font-semibold ml-auto">Merchant:</span>
          <span className="text-gray-800 font-medium">{merchantAccount || "\u2014"}</span>
        </div>
      </div>

      <div className="grid grid-cols-[1fr_1fr] gap-6">
        {/* LEFT — Form */}
        <div className="space-y-5">
          {/* Payment Details */}
          <Section title="Payment Details">
            <div className="grid grid-cols-2 gap-4">
              <Field label="Amount" required>
                <input type="number" min={0} step={0.01} value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0.00" className="field-input" />
              </Field>
              <Field label="Currency" required>
                <select value={currency} onChange={(e) => setCurrency(e.target.value)} className="field-input">
                  {CURRENCIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </Field>
            </div>
          </Section>

          {/* Tender Options */}
          <Section title="Tender Options">
            <ToggleRow label="Ask Gratuity" hint="Prompt the shopper to add a tip" checked={askGratuity} onChange={setAskGratuity} />
            <ToggleRow label="Receipt Handler" hint="Terminal handles receipt printing" checked={receiptHandler} onChange={setReceiptHandler} />
          </Section>

          {/* Force Entry Mode */}
          <Section title="Force Entry Mode">
            <div className="flex flex-wrap gap-2">
              {FORCE_ENTRY_MODES.map((mode) => (
                <label key={mode || "none"} className="cursor-pointer">
                  <input type="radio" name="forceEntry" value={mode} checked={forceEntry === mode} onChange={() => setForceEntry(mode)} className="hidden" />
                  <span className={`inline-block px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors ${forceEntry === mode ? "border-primary bg-blue-50 text-blue-700" : "border-gray-300 text-gray-600"}`}>
                    {FORCE_ENTRY_LABELS[mode] || mode}
                  </span>
                </label>
              ))}
            </div>
          </Section>

          {/* SaleToAcquirerData */}
          <Section title="SaleToAcquirerData">
            <Field label="Shopper Reference">
              <input type="text" value={shopperRef} onChange={(e) => setShopperRef(e.target.value)} placeholder="e.g. shopper_123" className="field-input" />
            </Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Recurring Contract">
                <select value={recurringContract} onChange={(e) => setRecurringContract(e.target.value)} className="field-input">
                  <option value="">&mdash; None &mdash;</option>
                  <option value="ONECLICK">ONECLICK</option>
                  <option value="RECURRING">RECURRING</option>
                  <option value="PAYOUT">PAYOUT</option>
                </select>
              </Field>
              <Field label="Authorisation Type">
                <select value={authType} onChange={(e) => setAuthType(e.target.value)} className="field-input">
                  <option value="">&mdash; None &mdash;</option>
                  <option value="PreAuth">PreAuth</option>
                  <option value="FinalAuth">FinalAuth</option>
                </select>
              </Field>
            </div>
            <Field label="Shopper Email">
              <input
                type="email"
                value={shopperEmail}
                onChange={(e) => setShopperEmail(e.target.value)}
                placeholder="e.g. shopper@example.com"
                className={`field-input ${!emailValid ? "!border-red-500" : ""}`}
              />
            </Field>
            <Field label="Store">
              <select value={store} onChange={(e) => setStore(e.target.value)} className="field-input">
                <option value="">&mdash; None &mdash;</option>
                {storeOptions.map((s) => (
                  <option key={s.reference} value={s.reference || ""}>{(s.reference || "") + (s.description ? ` \u2013 ${s.description}` : "")}</option>
                ))}
              </select>
            </Field>

            {/* Metadata */}
            <Field label="Metadata">
              <div className="space-y-2">
                {metadata.map((m, i) => (
                  <div key={i} className="flex gap-2 items-center">
                    <input type="text" placeholder="key" value={m.key} onChange={(e) => { const next = [...metadata]; next[i] = { ...next[i], key: e.target.value }; setMetadata(next); }} className="field-input flex-1" />
                    <input type="text" placeholder="value" value={m.value} onChange={(e) => { const next = [...metadata]; next[i] = { ...next[i], value: e.target.value }; setMetadata(next); }} className="field-input flex-1" />
                    <button type="button" onClick={() => setMetadata(metadata.filter((_, j) => j !== i))} className="text-gray-400 hover:text-red-500 text-lg">&times;</button>
                  </div>
                ))}
                <button type="button" onClick={() => setMetadata([...metadata, { key: "", value: "" }])} className="text-xs text-primary font-semibold hover:underline">+ Add entry</button>
              </div>
            </Field>
          </Section>

          <button
            type="button"
            onClick={handleSend}
            disabled={!formValid || sending}
            className="btn-primary w-full !h-11"
          >
            {sending ? "Sending\u2026" : "Send Payment Request"}
          </button>
        </div>

        {/* RIGHT — Preview */}
        <div className="sticky top-10 max-h-[calc(100vh-80px)] overflow-y-auto">
          <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-sm overflow-auto">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-400 font-sans font-semibold uppercase tracking-wide">Payload Preview</span>
              <button onClick={handleCopy} className="text-xs text-gray-400 hover:text-white border border-gray-700 rounded px-2 py-0.5 transition-colors">
                {copied ? "Copied!" : "Copy JSON"}
              </button>
            </div>
            <pre dangerouslySetInnerHTML={{ __html: syntaxHighlight(payload) }} />
            {acquirerData && (
              <div className="mt-3 pt-3 border-t border-gray-700">
                <span className="text-xs text-gray-500 font-sans font-semibold uppercase tracking-wide">Decoded SaleToAcquirerData</span>
                <pre className="mt-1" dangerouslySetInnerHTML={{ __html: syntaxHighlight(acquirerData) }} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h3 className="text-sm font-bold text-gray-700 mb-3">{title}</h3>
      <div className="space-y-3">{children}</div>
    </div>
  );
}

function Field({ label, required, children }: { label: string; required?: boolean; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-500 mb-1">
        {label}{required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      {children}
    </div>
  );
}

function ToggleRow({ label, hint, checked, onChange }: { label: string; hint: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <div className="text-sm font-medium text-gray-700">{label}</div>
        <div className="text-xs text-gray-400">{hint}</div>
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative w-10 h-5 rounded-full transition-colors ${checked ? "bg-primary" : "bg-gray-300"}`}
      >
        <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${checked ? "translate-x-5" : ""}`} />
      </button>
    </div>
  );
}
