"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiGet } from "@/lib/api";

export default function SessionsRedirectPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const redirectResult = searchParams.get("redirectResult") || searchParams.get("payload");
    if (!redirectResult) {
      setError("No redirect result found in URL parameters.");
      return;
    }

    apiGet<Record<string, unknown>>("/api/checkout/sessions/redirect", { redirectResult })
      .then((result) => {
        sessionStorage.setItem("checkout_result", JSON.stringify(result));
        router.push("/checkout/result");
      })
      .catch((err) => setError(err.message));
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="w-full max-w-[600px] text-center py-20">
        <p className="text-red-600 font-semibold mb-2">Redirect Error</p>
        <p className="text-sm text-gray-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-[600px] text-center py-20">
      <div className="flex items-center justify-center gap-3 text-gray-400">
        <div className="w-5 h-5 border-2 border-gray-300 border-t-primary rounded-full animate-spin" />
        <span>Processing redirect\u2026</span>
      </div>
    </div>
  );
}
