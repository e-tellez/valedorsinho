"use client";

import { useSearchParams } from "next/navigation";
import BackButton from "@/components/shared/BackButton";

export default function CardAcquisitionPage() {
  const searchParams = useSearchParams();
  const terminalId = searchParams.get("terminalId") || "";
  const merchantAccount = searchParams.get("merchantAccount") || "";

  return (
    <div className="w-full max-w-[700px]">
      <BackButton href="/terminal-payments" />
      <h1 className="text-2xl font-bold text-gray-900 mt-3 mb-2">Card Acquisition</h1>
      <p className="text-sm text-gray-500 mb-5">Acquire card details without charging.</p>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-3 text-xs text-gray-500 mb-4">
          <span className="font-semibold">Terminal:</span>
          <span className="text-gray-800 font-medium">{terminalId || "\u2014"}</span>
          <span className="font-semibold ml-auto">Merchant:</span>
          <span className="text-gray-800 font-medium">{merchantAccount || "\u2014"}</span>
        </div>
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg font-semibold mb-1">Coming Soon</p>
          <p className="text-sm">Card acquisition flow will be available in a future update.</p>
        </div>
      </div>
    </div>
  );
}
