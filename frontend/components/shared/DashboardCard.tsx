import Link from "next/link";

interface DashboardCardProps {
  href: string;
  icon: string;
  iconClass?: string;
  title: string;
  description: string;
}

export default function DashboardCard({
  href,
  icon,
  iconClass = "",
  title,
  description,
}: DashboardCardProps) {
  return (
    <Link
      href={href}
      className="block bg-white rounded-xl p-6 shadow-sm border border-gray-100
                 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200
                 no-underline text-inherit"
    >
      <div className={`text-3xl mb-3 ${iconClass}`}>{icon}</div>
      <h3 className="text-base font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-500 leading-relaxed">{description}</p>
    </Link>
  );
}
