"use client";

import { useState, useRef, useCallback, useMemo } from "react";
import { apiPost } from "@/lib/api";
import BackButton from "@/components/shared/BackButton";

interface ValidationError {
  field: string;
  error: string;
  rule: string;
}

const PLACEHOLDER = `{
  "merchantAccount": "YOUR_MERCHANT_ACCOUNT",
  "reference": "order-123",
  "amount": { "value": 1000, "currency": "EUR" },
  "paymentMethod": { "type": "scheme", "number": "..." },
  "returnUrl": "https://your-domain.com/redirect"
}`;

export default function PayloadValidatorPage() {
  const [input, setInput] = useState("");
  const [validating, setValidating] = useState(false);
  const [banner, setBanner] = useState<{ type: "success" | "error" | "loading"; message: string } | null>(null);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lineNumbersRef = useRef<HTMLDivElement>(null);

  const lineCount = useMemo(() => {
    const count = input ? input.split("\n").length : 1;
    return Math.max(count, 7);
  }, [input]);

  const handleScroll = useCallback(() => {
    if (textareaRef.current && lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  }, []);

  // Clear
  function handleClear() {
    setInput("");
    setBanner(null);
    setErrors([]);
    textareaRef.current?.focus();
  }

  // Validate
  async function handleValidate() {
    const raw = input.trim();
    if (!raw) {
      setBanner({ type: "error", message: "Please paste a JSON payload first." });
      return;
    }

    let payload: unknown;
    try {
      payload = JSON.parse(raw);
    } catch (e: any) {
      setBanner({ type: "error", message: "Invalid JSON: " + e.message });
      return;
    }

    setBanner({ type: "loading", message: "Validating against OpenAPI spec\u2026" });
    setValidating(true);

    try {
      const res = await apiPost<{ valid: boolean; errors?: ValidationError[] }>(
        "/api/tools/validate-payload",
        { payload },
      );

      if (res.valid) {
        setBanner({ type: "success", message: "Payload is valid \u2014 no errors found." });
        setErrors([]);
      } else {
        const errs = res.errors || [];
        setBanner({ type: "error", message: `${errs.length} validation error(s) found.` });
        setErrors(errs);
      }
    } catch (err: any) {
      setBanner({ type: "error", message: "Network error: " + err.message });
      setErrors([]);
    } finally {
      setValidating(false);
    }
  }

  // Export CSV
  function handleExportCsv() {
    if (!errors.length) return;
    const esc = (s: string) => String(s).replace(/"/g, '""');
    const header = "Field,Error,Rule";
    const rows = errors.map((e) => `"${esc(e.field)}","${esc(e.error)}","${esc(e.rule)}"`);
    const csv = [header, ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "payload_validation_errors.csv";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="w-full max-w-[1100px]">
      <BackButton href="/" />

      <h1 className="text-2xl font-bold text-gray-900 mt-3 mb-1">Payment Payload Validator</h1>
      <p className="text-sm text-gray-500 mb-5">
        Paste a <code className="bg-gray-100 px-1 rounded text-xs">/payments</code> JSON payload and validate it against the Adyen OpenAPI spec.
      </p>

      <div className="flex gap-6 items-start">
        {/* Left — Editor */}
        <div className="w-full max-w-[580px] shrink-0">
          <div className="bg-gray-900 text-gray-100 rounded-lg overflow-hidden flex flex-col" style={{ height: 580 }}>
            <div className="text-xs text-gray-400 font-sans font-semibold px-4 pt-3 pb-2 uppercase tracking-wide">
              /payments payload
            </div>
            <div className="flex flex-1 min-h-0">
              <div
                ref={lineNumbersRef}
                className="select-none text-right font-mono text-xs text-gray-600 overflow-hidden shrink-0"
                style={{
                  width: 44,
                  padding: "0 8px 0 12px",
                  lineHeight: "1.625rem",
                  whiteSpace: "pre",
                }}
              >
                {Array.from({ length: lineCount }, (_, i) => i + 1).join("\n")}
              </div>
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onScroll={handleScroll}
                placeholder={PLACEHOLDER}
                spellCheck={false}
                className="flex-1 bg-transparent text-gray-100 font-mono text-sm resize-none border-0 outline-none p-0 pr-4 placeholder-gray-600"
                style={{ lineHeight: "1.625rem", overflowY: "auto" }}
              />
            </div>
          </div>
        </div>

        {/* Right — Actions + Results */}
        <div className="flex-1 min-w-0 space-y-4">
          <div className="flex gap-3">
            <button onClick={handleValidate} disabled={validating} className="btn-primary">
              Validate
            </button>
            <button onClick={handleClear} className="btn-secondary">
              Clear
            </button>
            <button onClick={handleExportCsv} disabled={errors.length === 0} className="btn-secondary">
              Export CSV
            </button>
          </div>

          {/* Banner */}
          {banner && (
            <div
              className={`px-4 py-3 rounded-md text-sm font-medium ${
                banner.type === "success"
                  ? "bg-green-50 text-green-700 border border-green-200"
                  : banner.type === "loading"
                    ? "bg-blue-50 text-blue-700 border border-blue-200"
                    : "bg-red-50 text-red-700 border border-red-200"
              }`}
            >
              {banner.message}
            </div>
          )}

          {/* Errors table */}
          {errors.length > 0 && (
            <div>
              <h2 className="text-sm font-bold text-gray-700 mb-2">Validation Errors</h2>
              <div className="overflow-x-auto rounded-lg border border-gray-200">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                    <tr>
                      <th className="px-3 py-2 text-left">Field</th>
                      <th className="px-3 py-2 text-left">Error</th>
                      <th className="px-3 py-2 text-left">Rule</th>
                    </tr>
                  </thead>
                  <tbody>
                    {errors.map((e, i) => (
                      <tr key={i} className="border-t border-gray-100">
                        <td className="px-3 py-2 font-mono text-xs">{e.field}</td>
                        <td className="px-3 py-2">{e.error}</td>
                        <td className="px-3 py-2 text-xs text-gray-500">{e.rule}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
