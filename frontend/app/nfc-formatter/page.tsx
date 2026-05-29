"use client";

import { useState, useMemo } from "react";
import BackButton from "@/components/shared/BackButton";

const HEX_REGEX = /^[0-9a-fA-F]{12}$/;

function buildPayload(keyA: string, keyB: string, doInBackground: boolean) {
  return {
    cardAcquisition: [
      {
        conf: [
          {
            keys: [
              { key: keyA || "***", keyType: "a" },
              { key: keyB || "***", keyType: "b" },
            ],
            sector: 2,
          },
        ],
        convert: { dataType: "hex", length: 0, offset: 0 },
        ref: "mifareClassicCard",
      },
      {
        convert: { dataType: "hex", length: 0, offset: 0 },
        length: 256,
        offset: 0,
        ref: "type2Card",
      },
    ],
    doInBackground,
  };
}

export default function NfcFormatterPage() {
  const [keyA, setKeyA] = useState("");
  const [keyB, setKeyB] = useState("");
  const [doInBackground, setDoInBackground] = useState(true);
  const [copied, setCopied] = useState(false);

  const keyAValid = keyA === "" || HEX_REGEX.test(keyA);
  const keyBValid = keyB === "" || HEX_REGEX.test(keyB);

  const payload = useMemo(
    () => buildPayload(keyA.trim(), keyB.trim(), doInBackground),
    [keyA, keyB, doInBackground],
  );

  const payloadJson = JSON.stringify(payload, null, 2);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(payloadJson);
    } catch {
      // fallback
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
    const blob = new Blob([payloadJson], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "nfc_card_acquisition.json";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="w-full max-w-[1000px]">
      <BackButton href="/" />

      <div className="grid grid-cols-[1fr_1fr] gap-8 mt-4">
        {/* Left — Header + Form */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">NFC Formatter</h1>
          <p className="text-sm text-gray-500 mb-5">
            Configure NFC credentials for Mifare Classic 1K and generate the card acquisition payload.
          </p>

          <div className="space-y-4">
            {/* Key A */}
            <div>
              <label htmlFor="key-a" className="block text-sm font-semibold text-gray-700 mb-1">
                Key A <span className="text-gray-400 font-normal">(hex, e.g. FFFFFFFFFFFF)</span>
              </label>
              <input
                id="key-a"
                type="text"
                value={keyA}
                onChange={(e) => setKeyA(e.target.value)}
                placeholder="FFFFFFFFFFFF"
                maxLength={12}
                spellCheck={false}
                autoComplete="off"
                className={`field-input ${!keyAValid ? "!border-red-500" : ""}`}
              />
              {!keyAValid && <span className="text-xs text-red-500 mt-1 block">Must be a 12-character hex string.</span>}
            </div>

            {/* Key B */}
            <div>
              <label htmlFor="key-b" className="block text-sm font-semibold text-gray-700 mb-1">
                Key B <span className="text-gray-400 font-normal">(hex, e.g. FFFFFFFFFFFF)</span>
              </label>
              <input
                id="key-b"
                type="text"
                value={keyB}
                onChange={(e) => setKeyB(e.target.value)}
                placeholder="FFFFFFFFFFFF"
                maxLength={12}
                spellCheck={false}
                autoComplete="off"
                className={`field-input ${!keyBValid ? "!border-red-500" : ""}`}
              />
              {!keyBValid && <span className="text-xs text-red-500 mt-1 block">Must be a 12-character hex string.</span>}
            </div>

            {/* Checkbox */}
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={doInBackground}
                onChange={(e) => setDoInBackground(e.target.checked)}
                className="mt-1"
              />
              <div>
                <span className="block text-sm font-semibold text-gray-700">Turn off Adyen UI</span>
                <span className="block text-xs text-gray-400">Run card acquisition in the background without displaying the Adyen screen.</span>
              </div>
            </label>
          </div>

          {/* Actions */}
          <div className="flex gap-3 mt-5">
            <button onClick={handleCopy} className="btn-primary">Copy to Clipboard</button>
            <button onClick={handleDownload} className="btn-secondary">Download .json</button>
          </div>

          {copied && (
            <div className="mt-3 text-sm text-green-600 font-medium">Copied to clipboard!</div>
          )}
        </div>

        {/* Right — Preview */}
        <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-sm overflow-auto max-h-[calc(100vh-120px)] sticky top-10">
          <pre>{payloadJson}</pre>
        </div>
      </div>
    </div>
  );
}
