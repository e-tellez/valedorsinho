"use client";

import Link from "next/link";
import { useCheckout } from "@/context/CheckoutContext";
import { getIntegrationsByCategory } from "@/lib/constants";
import StepIndicator from "@/components/checkout/StepIndicator";
import BackButton from "@/components/shared/BackButton";

export default function SelectIntegrationPage() {
  const { state, setIntegration } = useCheckout();
  const categories = getIntegrationsByCategory();
  const displayAmount = (state.amountMinorUnits / 100).toFixed(2);

  return (
    <div className="bg-white rounded-lg shadow-md p-8 w-full max-w-[720px]">
      <StepIndicator currentStep={3} />

      <h1 className="text-xl font-bold text-gray-900 mb-2 text-center">Integration type</h1>
      <p className="text-sm text-gray-500 mb-5 text-center">Choose how you&apos;d like to pay.</p>

      {/* Order summary + manage cards */}
      <div className="flex items-center gap-4 mb-6">
        <div className="flex-1 bg-gray-50 border border-gray-200 rounded-md px-4 py-3 text-sm text-gray-600">
          <strong className="text-gray-900">Order total:</strong> {state.currency} {displayAmount}
          <br />
          <strong className="text-gray-900">Shopper:</strong> {state.shopperReference || "Guest"}
          <br />
          <strong className="text-gray-900">Country:</strong> {state.countryCode}
        </div>
        {state.shopperReference && (
          <Link
            href="/checkout/manage-payments"
            className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-gray-600 border border-gray-300 rounded-lg no-underline whitespace-nowrap transition-colors hover:border-primary hover:bg-blue-50"
          >
            <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              <rect x={1} y={4} width={22} height={16} rx={2} ry={2} />
              <line x1={1} y1={10} x2={23} y2={10} />
            </svg>
            Manage cards
          </Link>
        )}
      </div>

      {/* Integration categories – two columns */}
      <div className="grid grid-cols-2 gap-6">
        {categories.map((category) => (
          <div key={category.name}>
            <h2 className="text-base font-bold text-gray-600 mb-3 pb-1.5 border-b-2 border-gray-200 text-center">
              {category.name}
            </h2>
            <ul className="list-none flex flex-col gap-3">
              {category.integrations.map((integration) => (
                <li key={integration.href} className="border border-gray-200 rounded-lg transition-all duration-150 hover:border-primary hover:shadow-md">
                  <Link
                    href={integration.href}
                    onClick={() => setIntegration(`${integration.name} (${category.name})`)}
                    className="flex items-center justify-between p-4 no-underline text-inherit gap-3"
                  >
                    <div className="flex flex-col gap-1">
                      <span className="text-base font-bold text-gray-900">{integration.name}</span>
                      <span className="text-xs text-gray-500 leading-snug">
                        {integration.note && <p className="mb-0.5">{integration.note}</p>}
                        {integration.description}
                      </span>
                    </div>
                    <span className="text-xl text-gray-400 shrink-0">&rsaquo;</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <BackButton href="/checkout/order" label="Back" />
    </div>
  );
}
