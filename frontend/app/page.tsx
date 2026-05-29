import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Valedorsinho – Dashboard",
};

/* ------------------------------------------------------------------ */
/* SVG icon components                                                  */
/* ------------------------------------------------------------------ */

function CreditCardIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <rect x={1} y={4} width={22} height={16} rx={2} ry={2} />
      <line x1={1} y1={10} x2={23} y2={10} />
    </svg>
  );
}

function DocumentIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1={16} y1={13} x2={8} y2={13} />
      <line x1={16} y1={17} x2={8} y2={17} />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  );
}

function CheckSquareIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <path d="M9 11l3 3L22 4" />
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
    </svg>
  );
}

function MonitorIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <rect x={2} y={3} width={20} height={14} rx={2} ry={2} />
      <line x1={8} y1={21} x2={16} y2={21} />
      <line x1={12} y1={17} x2={12} y2={21} />
    </svg>
  );
}

function BoxIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <rect x={2} y={7} width={20} height={14} rx={2} ry={2} />
      <path d="M16 3h-8l-2 4h12l-2-4z" />
    </svg>
  );
}

function NfcIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <path d="M2 7v-2a2 2 0 0 1 2-2h4" />
      <path d="M22 7v-2a2 2 0 0 0-2-2h-4" />
      <path d="M2 17v2a2 2 0 0 0 2 2h4" />
      <path d="M22 17v2a2 2 0 0 1-2 2h-4" />
      <path d="M8 12h.01" />
      <path d="M12 12h.01" />
      <path d="M16 12h.01" />
    </svg>
  );
}

function GearIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <circle cx={12} cy={12} r={3} />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  );
}

function EditIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}

/* ------------------------------------------------------------------ */
/* Dashboard Card                                                       */
/* ------------------------------------------------------------------ */

interface CardProps {
  href?: string;
  icon: React.ReactNode;
  iconClass: string;
  title: string;
  description: string;
  badge?: string;
  badgeClass?: string;
  disabled?: boolean;
}

function DashCard({ href, icon, iconClass, title, description, badge, badgeClass, disabled }: CardProps) {
  const content = (
    <>
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${iconClass}`}>
        <div className="w-[22px] h-[22px]">{icon}</div>
      </div>
      <div className="flex-1 min-w-0 flex flex-col gap-0.5">
        <span className="text-[0.95rem] font-bold text-[#1a1a1a]">{title}</span>
        <span className="text-[0.8rem] text-[#666] leading-[1.4]">{description}</span>
        {badge && (
          <span className={`inline-block mt-1 px-2 py-[2px] text-[0.68rem] font-semibold rounded-[10px] w-fit ${badgeClass}`}>
            {badge}
          </span>
        )}
      </div>
      {!disabled && <span className="shrink-0 text-[1.4rem] text-[#aaa]">&rsaquo;</span>}
    </>
  );

  const base =
    "flex items-center gap-[14px] bg-white rounded-[10px] py-[18px] px-4 border border-[#e5e5e5] no-underline text-inherit transition-all duration-150 cursor-pointer";
  const interactive = disabled
    ? " opacity-60 !cursor-default hover:border-[#e5e5e5] hover:shadow-none hover:bg-white"
    : " hover:border-primary hover:shadow-[0_0_0_3px_rgba(0,112,243,0.1)] hover:bg-[#f8fbff]";

  if (disabled || !href) {
    return <div className={base + interactive}>{content}</div>;
  }

  return (
    <Link href={href} className={base + interactive}>
      {content}
    </Link>
  );
}

/* ------------------------------------------------------------------ */
/* Page                                                                 */
/* ------------------------------------------------------------------ */

export default function DashboardPage() {
  return (
    <div className="w-full max-w-[840px]">
      {/* Header */}
      <header className="text-center mb-8">
        <h1 className="text-[1.8rem] font-bold text-[#1a1a1a] mb-1">Valedorsinho</h1>
        <p className="text-[0.95rem] text-[#666]">Adyen Unified Commerce Toolbox</p>
      </header>

      {/* Two-column section: Digital | Unified Commerce */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Digital */}
        <div>
          <h2 className="text-[1.05rem] font-bold uppercase tracking-[0.06em] text-[#888] pb-1 border-b-2 border-[#e5e5e5] text-center mb-3">Digital</h2>
          <div className="flex flex-col gap-3">
            <DashCard href="/checkout" icon={<CreditCardIcon />} iconClass="bg-[#e8f0fe] text-[#0070f3]" title="Checkout" description="Drop-in & Components integration demos." badge="WIP" badgeClass="bg-[#fff3e0] text-[#e67e22]" />
            <DashCard href="/payload-suggested" icon={<DocumentIcon />} iconClass="bg-[#e8f0fe] text-[#0070f3]" title="Payload Suggested" description="Recommended payloads per vertical." badge="WIP" badgeClass="bg-[#fff3e0] text-[#e67e22]" />
            <DashCard href="/payload-validator" icon={<CheckSquareIcon />} iconClass="bg-[#e8f0fe] text-[#0070f3]" title="Payload Validator" description="Validate payloads against Adyen OpenAPI specs." badge="WIP" badgeClass="bg-[#fff3e0] text-[#e67e22]" />
          </div>
        </div>

        {/* Unified Commerce */}
        <div>
          <h2 className="text-[1.05rem] font-bold uppercase tracking-[0.06em] text-[#888] pb-1 border-b-2 border-[#e5e5e5] text-center mb-3">Unified Commerce</h2>
          <div className="flex flex-col gap-3">
            <DashCard href="/terminal-payments" icon={<MonitorIcon />} iconClass="bg-[#e6f7ed] text-[#1a8a4a]" title="Terminal Payments" description="Send payment requests to in-person terminals." badge="WIP" badgeClass="bg-[#fff3e0] text-[#e67e22]" />
            <DashCard href="/terminal-fleet" icon={<BoxIcon />} iconClass="bg-[#e6f7ed] text-[#1a8a4a]" title="Terminal Fleet Manager" description="Manage and monitor your terminal fleet." badge="WIP" badgeClass="bg-[#fff3e0] text-[#e67e22]" />
            <DashCard href="/nfc-formatter" icon={<NfcIcon />} iconClass="bg-[#e6f7ed] text-[#1a8a4a]" title="NFC Formatter" description="Configure NFC tap-to-pay credentials." badge="WIP" badgeClass="bg-[#fff3e0] text-[#e67e22]" />
          </div>
        </div>
      </div>

      {/* Additional Tools */}
      <div>
        <h2 className="text-[1.05rem] font-bold uppercase tracking-[0.06em] text-[#888] pb-1 border-b-2 border-[#e5e5e5] text-center mb-3 col-span-full">Additional Tools</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DashCard href="/setup" icon={<GearIcon />} iconClass="bg-[#f0f0f0] text-[#999]" title="Set Up" description="Configure Adyen credentials, merchant account and webhook settings." />
          <DashCard href="/management-api" icon={<EditIcon />} iconClass="bg-[#f0f0f0] text-[#999]" title="Management API" description="Explore and interact with the Adyen Management API." badge="WIP" badgeClass="bg-[#fff3e0] text-[#e67e22]" />
          <DashCard disabled icon={<ChatIcon />} iconClass="bg-[#f0f0f0] text-[#999]" title="Webhook Logs" description="Monitor incoming webhook notifications in real time." badge="Coming soon" badgeClass="bg-[#f0f0f0] text-[#888]" />
        </div>
      </div>
    </div>
  );
}
