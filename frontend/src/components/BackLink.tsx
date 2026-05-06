import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import type { ReactNode } from "react";

interface BackLinkProps {
  href: string;
  children: ReactNode;
}

export default function BackLink({ href, children }: BackLinkProps) {
  return (
    <Link
      href={href}
      className="inline-flex items-center gap-space-xs font-label text-label text-secondary hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus-ring focus-visible:ring-offset-2 rounded-sm transition-colors motion-reduce:transition-none"
    >
      <ChevronLeft className="w-4 h-4" aria-hidden="true" />
      <span>{children}</span>
    </Link>
  );
}
