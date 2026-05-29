"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCheckout } from "@/context/CheckoutContext";
import StepIndicator from "@/components/checkout/StepIndicator";
import BackButton from "@/components/shared/BackButton";

export default function ChooseFlowPage() {
  const router = useRouter();
  const { setFlow, reset } = useCheckout();

  function handleGuest() {
    setFlow(true);
    router.push("/checkout/order");
  }

  function handleAccount() {
    setFlow(false);
    router.push("/checkout/order");
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-8 w-full max-w-[720px]">
      <StepIndicator currentStep={1} />

      <h1 className="text-xl font-bold text-gray-900 mb-2">How would you like to pay?</h1>
      <p className="text-sm text-gray-500 mb-5">Choose a checkout experience to get started.</p>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <button onClick={handleGuest} className="flex flex-col items-center justify-center text-center p-6 border-2 border-gray-200 rounded-xl no-underline text-inherit transition-all duration-150 cursor-pointer hover:border-primary hover:shadow-md hover:bg-blue-50/30 bg-white">
          <svg className="w-12 h-12 text-primary mb-3" viewBox="0 0 48 48" fill="none">
            <circle cx={24} cy={16} r={8} stroke="currentColor" strokeWidth={2.5} />
            <path d="M8 42c0-8.837 7.163-16 16-16s16 7.163 16 16" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" />
          </svg>
          <span className="text-base font-bold text-gray-900 mb-1">Guest</span>
          <span className="text-xs text-gray-500 leading-snug">Pay without creating an account. Quick and simple.</span>
        </button>

        <button onClick={handleAccount} className="flex flex-col items-center justify-center text-center p-6 border-2 border-gray-200 rounded-xl no-underline text-inherit transition-all duration-150 cursor-pointer hover:border-primary hover:shadow-md hover:bg-blue-50/30 bg-white">
          <svg className="w-12 h-12 text-primary mb-3" viewBox="0 0 48 48" fill="none">
            <circle cx={20} cy={16} r={8} stroke="currentColor" strokeWidth={2.5} />
            <path d="M4 42c0-8.837 7.163-16 16-16s16 7.163 16 16" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" />
            <circle cx={38} cy={32} r={8} fill="#e8f0fe" stroke="currentColor" strokeWidth={2} />
            <path d="M35 32l2 2 4-4" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span className="text-base font-bold text-gray-900 mb-1">Account</span>
          <span className="text-xs text-gray-500 leading-snug">Sign in to save cards and speed up future payments.</span>
        </button>
      </div>

      <BackButton href="/" onClick={reset} />
    </div>
  );
}
