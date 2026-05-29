import Link from "next/link";

export default function NotFound() {
  return (
    <div className="text-center py-20">
      <h1 className="text-6xl font-bold text-gray-300 mb-4">404</h1>
      <p className="text-gray-500 mb-6">Page not found</p>
      <Link href="/" className="btn-primary inline-block leading-10">
        Back to Dashboard
      </Link>
    </div>
  );
}
