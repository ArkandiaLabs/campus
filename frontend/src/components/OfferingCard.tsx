import Link from "next/link";
import type { UserOffering } from "@/types";

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "";
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("es-MX", { day: "numeric", month: "long", year: "numeric" });
}

interface OfferingCardProps {
  offering: UserOffering;
}

export default function OfferingCard({ offering }: OfferingCardProps) {
  const dateRange =
    offering.start_date && offering.end_date
      ? `${formatDate(offering.start_date)} — ${formatDate(offering.end_date)}`
      : offering.cohort_title ?? "";

  return (
    <Link
      href={`/products/${offering.id}`}
      className="block border border-gray-200 rounded-lg p-5 hover:border-blue-600 hover:shadow-sm transition-all"
    >
      <h2 className="text-base font-semibold text-gray-900 mb-1">{offering.title}</h2>
      {dateRange && <p className="text-sm text-gray-500">{dateRange}</p>}
    </Link>
  );
}
