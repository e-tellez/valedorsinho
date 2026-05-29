"use client";

import { useState, useMemo } from "react";
import BackButton from "@/components/shared/BackButton";
import { VERTICALS } from "@/lib/verticals";

function deepMerge(
  target: Record<string, unknown>,
  source: Record<string, unknown>,
): Record<string, unknown> {
  const result = { ...target };
  for (const key of Object.keys(source)) {
    if (
      result[key] &&
      typeof result[key] === "object" &&
      !Array.isArray(result[key]) &&
      typeof source[key] === "object" &&
      !Array.isArray(source[key])
    ) {
      result[key] = deepMerge(
        result[key] as Record<string, unknown>,
        source[key] as Record<string, unknown>,
      );
    } else {
      result[key] = source[key];
    }
  }
  return result;
}

export default function PayloadSuggestedPage() {
  const [selected, setSelected] = useState<Set<string>>(new Set([VERTICALS[0].key]));
  const [copied, setCopied] = useState(false);

  const merged = useMemo(() => {
    if (selected.size === 0) return null;
    let result: Record<string, unknown> = {};
    VERTICALS.forEach((v) => {
      if (selected.has(v.key)) {
        result = deepMerge(result, v.payload);
      }
    });
    return result;
  }, [selected]);

  const payloadJson = merged ? JSON.stringify(merged, null, 2) : "";

  function toggleVertical(key: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }

  async function handleCopy() {
    if (!payloadJson) return;
    try {
      await navigator.clipboard.writeText(payloadJson);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = payloadJson;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleDownload() {
    if (!payloadJson) return;
    const keys = Array.from(selected).join("_");
    const blob = new Blob([payloadJson], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `payload_${keys || "empty"}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="w-full max-w-[1000px]">
      <BackButton href="/" />

      <h1 className="text-2xl font-bold text-gray-900 mt-3 mb-1">Payload Suggested</h1>
      <p className="text-sm text-gray-500 mb-5">
        Select one or more merchant verticals to generate a recommended{" "}
        <code className="bg-gray-100 px-1 rounded text-xs">/payments</code> payload.
      </p>

      {/* Vertical checkboxes */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        {VERTICALS.map((v) => {
          const isChecked = selected.has(v.key);
          return (
            <label
              key={v.key}
              className={`flex items-start gap-3 cursor-pointer rounded-xl border p-4 transition-colors ${
                isChecked
                  ? "border-primary bg-blue-50/40"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <input
                type="checkbox"
                checked={isChecked}
                onChange={() => toggleVertical(v.key)}
                className="mt-0.5"
              />
              <div>
                <span className="block text-sm font-semibold text-gray-800">{v.label}</span>
                <span className="block text-xs text-gray-500 mt-0.5">{v.description}</span>
              </div>
            </label>
          );
        })}
      </div>

      {/* Actions */}
      <div className="flex gap-3 mb-4">
        <button onClick={handleCopy} className="btn-primary">Copy to Clipboard</button>
        <button onClick={handleDownload} className="btn-secondary">Download .json</button>
      </div>

      {copied && (
        <div className="mb-4 text-sm text-green-600 font-medium">Copied to clipboard!</div>
      )}

      {/* Preview */}
      <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-sm overflow-auto max-h-[500px]">
        <pre>{payloadJson || "Select at least one vertical."}</pre>
      </div>
    </div>
  );
}
