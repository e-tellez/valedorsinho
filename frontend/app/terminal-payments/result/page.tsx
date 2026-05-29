"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

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

interface PaymentResultData {
  success: boolean;
  resultTitle: string;
  resultMessage?: string;
  decodedAdditionalResponse?: Record<string, unknown> | string | null;
  paymentSummary?: Array<{ label: string; value: string }>;
  responseJson?: unknown;
}

export default function TerminalPaymentResultPage() {
  const searchParams = useSearchParams();
  const terminalId = searchParams.get("terminalId") || "";
  const merchantAccount = searchParams.get("merchantAccount") || "";

  const [data, setData] = useState<PaymentResultData | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const raw = sessionStorage.getItem("terminal_payment_result");
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw);
      setData(parsed);
    } catch {}
    sessionStorage.removeItem("terminal_payment_result");
  }, []);

  function handleCopy() {
    if (!data?.responseJson) return;
    navigator.clipboard.writeText(JSON.stringify(data.responseJson, null, 2)).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  if (!data) {
    return (
      <div className="w-full max-w-[900px] text-center py-20">
        <p className="text-gray-500">No payment result data found.</p>
        <Link href="/terminal-payments" className="text-primary underline text-sm mt-2 inline-block">
          Back to Terminal Payments
        </Link>
      </div>
    );
  }

  const backHref = `/terminal-payments/make-payment?terminalId=${encodeURIComponent(terminalId)}&merchantAccount=${encodeURIComponent(merchantAccount)}`;
  const hasDecoded = data.decodedAdditionalResponse != null;

  return (
    <div className={`w-full ${hasDecoded ? "max-w-[1400px]" : "max-w-[900px]"}`}>
      <header className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900">Payment Result</h1>
        <p className="text-sm text-gray-500">Terminal API response for your payment request.</p>
      </header>

      <div className="flex gap-3 mb-5">
        <Link href={backHref} className="btn-primary !inline-flex !w-auto px-5 text-sm">
          &larr; Make Another Payment
        </Link>
        <Link href="/terminal-payments" className="btn-secondary !inline-flex !w-auto px-5 text-sm">
          &larr; Back to Terminal Payments
        </Link>
      </div>

      {/* Banner + Summary */}
      <div className={`max-w-[700px] mx-auto rounded-xl border overflow-hidden mb-5 ${data.success ? "border-green-200" : "border-red-200"}`}>
        <div className={`flex items-center justify-center gap-3 px-6 py-4 text-white ${data.success ? "bg-green-600" : "bg-red-600"}`}>
          <span className="text-2xl">{data.success ? "\u2713" : "\u2717"}</span>
          <span className="text-lg font-bold">{data.resultTitle}</span>
        </div>

        {data.resultMessage && (
          <div className="text-center text-sm text-gray-500 px-5 pt-2">{data.resultMessage}</div>
        )}

        {data.paymentSummary && data.paymentSummary.length > 0 && (
          <div className="grid grid-cols-[repeat(auto-fill,minmax(180px,1fr))] gap-2.5 px-5 py-4">
            {data.paymentSummary.map((item, i) => (
              <div key={i}>
                <div className="text-[0.68rem] font-semibold text-gray-400 uppercase tracking-wider">{item.label}</div>
                <div className="text-sm font-semibold text-gray-900 mt-0.5">{item.value}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Two-column: full response + decoded */}
      <div className={`grid gap-5 mt-5 ${hasDecoded ? "grid-cols-2" : "grid-cols-1"}`}>
        {/* Full Response */}
        {data.responseJson && (
          <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-sm overflow-auto max-h-[600px]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-400 font-sans font-semibold uppercase tracking-wide">Full Response</span>
              <button onClick={handleCopy} className="text-xs text-gray-400 hover:text-white border border-gray-700 rounded px-2 py-0.5 transition-colors">
                {copied ? "Copied!" : "Copy JSON"}
              </button>
            </div>
            <pre dangerouslySetInnerHTML={{ __html: syntaxHighlight(data.responseJson) }} />
          </div>
        )}

        {/* Decoded Additional Response */}
        {hasDecoded && (
          <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-sm overflow-auto max-h-[600px]">
            <div className="mb-1">
              <span className="text-xs text-gray-400 font-sans font-semibold uppercase tracking-wide">Decoded Additional Response</span>
            </div>
            <div className="text-[0.7rem] text-gray-500 font-sans mb-2">Base64-decoded per nexo EPAS standard</div>
            <pre dangerouslySetInnerHTML={{ __html: syntaxHighlight(data.decodedAdditionalResponse) }} />
          </div>
        )}
      </div>
    </div>
  );
}
