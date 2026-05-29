import Link from "next/link";

interface BackButtonProps {
  href: string;
  label?: string;
  onClick?: () => void;
}

export default function BackButton({
  href,
  label = "Back to Dashboard",
  onClick,
}: BackButtonProps) {
  return (
    <Link href={href} onClick={onClick} className="btn-back">
      <span aria-hidden="true">&larr;</span> {label}
    </Link>
  );
}
