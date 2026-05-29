import type { Metadata } from "next";
import Link from "next/link";
import BackButton from "@/components/shared/BackButton";

export const metadata: Metadata = {
  title: "Management API – Valedorsinho",
};

/* ------------------------------------------------------------------ */
/* SVG icons                                                            */
/* ------------------------------------------------------------------ */

function UserIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx={12} cy={7} r={4} />
    </svg>
  );
}

function UsersIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx={9} cy={7} r={4} />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function CreditCardIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <rect x={1} y={4} width={22} height={16} rx={2} ry={2} />
      <line x1={1} y1={10} x2={23} y2={10} />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <rect x={3} y={11} width={18} height={11} rx={2} ry={2} />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  );
}

function WebhookIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
      <path d="M10 15l-5.878 5.878a2.684 2.684 0 0 1-3.798-3.798L7 11" />
      <path d="M15.05 5C13.16 5 11.5 6.57 11.5 8.5c0 1.38.81 2.57 2 3.13" />
      <path d="M22 2l-1.5 1.5" />
      <path d="M18 6l2-2" />
      <polyline points="15 3 18 3 18 6" />
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

/* ------------------------------------------------------------------ */
/* Page                                                                 */
/* ------------------------------------------------------------------ */

const SECTIONS = [
  { icon: <UserIcon />, iconClass: "bg-blue-50 text-blue-600", title: "Account", description: "View and manage merchant account details." },
  { icon: <UsersIcon />, iconClass: "bg-blue-50 text-blue-600", title: "Users", description: "Manage users and their roles." },
  { icon: <CreditCardIcon />, iconClass: "bg-blue-50 text-blue-600", title: "Payment Methods", description: "Configure available payment methods." },
  { icon: <LockIcon />, iconClass: "bg-blue-50 text-blue-600", title: "API Credentials", description: "Manage API keys and credential settings." },
  { icon: <WebhookIcon />, iconClass: "bg-blue-50 text-blue-600", title: "Webhooks", description: "Configure and test webhook endpoints." },
  { icon: <MonitorIcon />, iconClass: "bg-green-50 text-green-600", title: "Terminals", description: "View and manage terminal devices." },
];

export default function ManagementApiPage() {
  return (
    <div className="w-full max-w-[900px]">
      <BackButton href="/" />

      <h1 className="text-2xl font-bold text-gray-900 mt-4 mb-1">Management API</h1>
      <p className="text-sm text-gray-500 mb-6">
        Explore and interact with the Adyen Management API.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {SECTIONS.map((section) => (
          <Link
            key={section.title}
            href="#"
            className="flex items-center gap-4 bg-white rounded-xl p-4 border border-gray-100
                       no-underline text-inherit transition-all duration-200
                       hover:shadow-md hover:-translate-y-0.5"
          >
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${section.iconClass}`}>
              <div className="w-5 h-5">{section.icon}</div>
            </div>
            <div className="flex-1 min-w-0">
              <span className="block text-[0.95rem] font-semibold text-gray-900">
                {section.title}
              </span>
              <span className="block text-sm text-gray-500 leading-snug mt-0.5">
                {section.description}
              </span>
            </div>
            <span className="text-gray-300 text-xl font-light">&rsaquo;</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
