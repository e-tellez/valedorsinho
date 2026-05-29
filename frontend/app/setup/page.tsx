import type { Metadata } from "next";
import BackButton from "@/components/shared/BackButton";

export const metadata: Metadata = {
  title: "Set Up – Valedorsinho",
};

export default function SetupPage() {
  return (
    <div className="w-full max-w-[540px]">
      <BackButton href="/" />

      <h1 className="text-2xl font-bold text-gray-900 mt-4 mb-1">Set Up</h1>
      <p className="text-sm text-gray-500 mb-6">
        Configure your Adyen credentials and environment settings.
      </p>

      <form className="bg-white rounded-xl border border-gray-200 p-7 space-y-5">
        {/* API Key */}
        <FieldRow label="API Key">
          <input
            type="password"
            id="adyen_api_key"
            name="adyen_api_key"
            placeholder="AQE..."
            autoComplete="off"
            className="field-input"
          />
        </FieldRow>

        {/* Client Key */}
        <FieldRow label="Client Key">
          <input
            type="text"
            id="adyen_client_key"
            name="adyen_client_key"
            placeholder="test_..."
            autoComplete="off"
            className="field-input"
          />
        </FieldRow>

        {/* Merchant Account */}
        <FieldRow label="Merchant Account">
          <input
            type="text"
            id="adyen_merchant_account"
            name="adyen_merchant_account"
            placeholder="YourMerchantAccountECOM"
            autoComplete="off"
            className="field-input"
          />
        </FieldRow>

        {/* Environment */}
        <FieldRow label="Environment">
          <select
            id="adyen_environment"
            name="adyen_environment"
            defaultValue="test"
            className="field-input"
          >
            <option value="test">Test</option>
          </select>
        </FieldRow>

        {/* Webhook URL */}
        <FieldRow label="Webhook URL">
          <input
            type="url"
            id="webhook_url"
            name="webhook_url"
            placeholder="https://your-domain.com/webhooks"
            autoComplete="off"
            className="field-input"
          />
        </FieldRow>

        {/* HMAC Key (disabled) */}
        <FieldRow label="HMAC Key" disabled>
          <input
            type="text"
            id="hmac_key"
            name="hmac_key"
            placeholder="Coming soon"
            disabled
            className="field-input disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed disabled:border-gray-200"
          />
          <span className="block mt-1 text-xs text-gray-400">
            Webhook signature verification – not yet available.
          </span>
        </FieldRow>

        {/* Store ID (disabled) */}
        <FieldRow label="Store ID" disabled>
          <input
            type="text"
            id="store_id"
            name="store_id"
            placeholder="Coming soon"
            disabled
            className="field-input disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed disabled:border-gray-200"
          />
          <span className="block mt-1 text-xs text-gray-400">
            Required for Unified Commerce features – not yet available.
          </span>
        </FieldRow>

        <button type="submit" className="btn-primary w-full !h-11 mt-2" disabled>
          Save Configuration
        </button>
        <p className="text-xs text-gray-400 text-center">
          Saving is not yet implemented. Configuration is read from the .env file.
        </p>
      </form>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Field row sub-component                                              */
/* ------------------------------------------------------------------ */

function FieldRow({
  label,
  disabled,
  children,
}: {
  label: string;
  disabled?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className={disabled ? "opacity-60" : ""}>
      <label className="block text-[0.85rem] font-semibold text-gray-600 mb-1.5">
        {label}
      </label>
      {children}
    </div>
  );
}
