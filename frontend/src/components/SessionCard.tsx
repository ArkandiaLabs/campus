import Link from "next/link";
import { ChevronRight } from "lucide-react";
import type { SessionSummary } from "@/types";
import { formatSessionMeta } from "@/lib/format";

interface SessionCardProps {
  offeringId: string;
  session: SessionSummary;
}

export default function SessionCard({ offeringId, session }: SessionCardProps) {
  const meta = formatSessionMeta(session.scheduled_at, session.duration_minutes);

  return (
    <Link
      href={`/products/${offeringId}/sessions/${session.id}`}
      className="flex items-center gap-space-md bg-surface rounded-md border border-secondary/20 p-space-md min-h-11 hover:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus-ring focus-visible:ring-offset-2 active:opacity-80 transition-colors motion-reduce:transition-none"
    >
      <div className="flex-1 min-w-0">
        <h3 className="font-body text-body font-bold text-foreground mb-space-xs">
          {session.title}
        </h3>
        <p className="font-label text-label text-secondary">{meta}</p>
      </div>
      <ChevronRight
        className="w-5 h-5 text-secondary flex-shrink-0"
        aria-hidden="true"
      />
    </Link>
  );
}
