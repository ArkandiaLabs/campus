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
      className="block bg-surface rounded-md p-md border border-secondary/20 hover:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus-ring transition-colors"
    >
      <h2 className="font-h2 text-h2 text-foreground mb-xs">{offering.title}</h2>
      {dateRange && (
        <p className="font-label text-label text-secondary">{dateRange}</p>
      )}
    </Link>
  );
}