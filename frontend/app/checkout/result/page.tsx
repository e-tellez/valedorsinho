"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { useCheckout } from "@/context/CheckoutContext";

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

export default function ResultPage() {
  const searchParams = useSearchParams();
  const status = searchParams.get("status") ?? "failure";
  const resultCode = searchParams.get("resultCode") ?? "Unknown";
  const pspReference = searchParams.get("pspReference") ?? "";
  const integrationType = searchParams.get("integrationType") ?? "";

  const isSuccess = status === "success";
  const { reset } = useCheckout();

  const [responseHtml, setResponseHtml] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    reset();
    const raw = sessionStorage.getItem("adyen_result");
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw);
      setResponseHtml(syntaxHighlight(parsed));
    } catch {}
    sessionStorage.removeItem("adyen_result");
  }, []);

  function handleCopy() {
    const raw = document.getElementById("response-json")?.textContent;
    if (!raw) return;
    navigator.clipboard.writeText(raw).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  // Parse integration type into badges
  const integrationName = integrationType.split(" (")[0] || "";
  const integrationFlow = integrationType.includes("Sessions") ? "Sessions" : "Advanced";

  return (
    <div className="flex gap-6 items-start w-full max-w-[1200px]">
      {/* Result card */}
      <div className={`bg-white rounded-lg shadow-md p-8 w-full max-w-[480px] shrink-0 text-center border-t-4 ${isSuccess ? "border-green-500" : "border-red-500"}`}>
        <div className="text-5xl mb-4">{isSuccess ? "✅" : "❌"}</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-3">
          {isSuccess ? "Payment successful" : "Payment failed"}
        </h1>

        {integrationName && (
          <div className="flex gap-2 justify-center mb-4">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700">
              {integrationName}
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-50 text-green-700">
              {integrationFlow}
            </span>
          </div>
        )}

        <p className="text-sm text-gray-600 mb-4">
          Raw acquirer response:{" "}
          <strong className={isSuccess ? "text-green-700" : "text-red-600"}>
            {resultCode}
          </strong>
        </p>

        {pspReference && (
          <div className="bg-gray-50 border border-gray-200 rounded-md px-4 py-3 mb-6 inline-block">
            <span className="block text-xs text-gray-500 uppercase tracking-wide font-semibold">PSP Reference</span>
            <span className="block text-base font-mono text-gray-900 mt-1">{pspReference}</span>
          </div>
        )}

        <div className="flex gap-3 justify-center items-center mt-4">
          <Link href="/checkout" className="btn-primary !inline-flex items-center justify-center !w-auto px-6 no-underline">
            Try again
          </Link>
          <Link href="/" className="btn-secondary !inline-flex items-center justify-center !w-auto px-6 no-underline">
            Homepage
          </Link>
        </div>
      </div>

      {/* Response sidebar */}
      {responseHtml && (
        <div className="flex-1 min-w-0 sticky top-10 max-h-[calc(100vh-80px)] overflow-y-auto">
          <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-sm overflow-auto">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-400 font-sans font-semibold uppercase tracking-wide">
                Full Adyen response
              </span>
              <button
                onClick={handleCopy}
                className="text-xs text-gray-400 hover:text-white border border-gray-700 rounded px-2 py-0.5 transition-colors"
              >
                {copied ? "Copied!" : "Copy JSON"}
              </button>
            </div>
            <pre id="response-json" dangerouslySetInnerHTML={{ __html: responseHtml }} />
          </div>
        </div>
      )}
    </div>
  );
}
