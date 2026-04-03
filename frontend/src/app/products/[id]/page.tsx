import { notFound, redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase";
import Navbar from "@/components/Navbar";
import ContentList from "@/components/ContentList";
import type { OfferingDetail } from "@/types";

async function getOffering(token: string, id: string): Promise<OfferingDetail | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const res = await fetch(`${apiUrl}/api/v1/catalog/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (res.status === 404) return null;
  if (!res.ok) return null;
  return res.json() as Promise<OfferingDetail>;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "";
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("es-MX", { day: "numeric", month: "long", year: "numeric" });
}

interface ProductPageProps {
  params: Promise<{ id: string }>;
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { id } = await params;

  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    redirect("/login");
  }

  const offering = await getOffering(session.access_token, id);

  if (!offering) {
    notFound();
  }

  const dateRange =
    offering.start_date && offering.end_date
      ? `${formatDate(offering.start_date)} — ${formatDate(offering.end_date)}`
      : offering.cohort_title ?? "";

  const userName =
    (user.user_metadata?.full_name as string | undefined) ?? user.email ?? "";

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar userName={userName} />

      <main className="max-w-3xl mx-auto w-full px-4 py-8">
        {/* Offering header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-1">{offering.title}</h1>
          {dateRange && <p className="text-sm text-gray-500 mb-2">{dateRange}</p>}
          {offering.description && (
            <p className="text-gray-600 text-sm">{offering.description}</p>
          )}
        </div>

        {/* Content list with progress */}
        {offering.contents.length > 0 ? (
          <ContentList
            offeringId={offering.id}
            initialContents={offering.contents}
            totalContents={offering.total_contents}
            completedContents={offering.completed_contents}
          />
        ) : (
          <p className="text-gray-500 text-sm">
            Aun no hay contenido disponible para este workshop.
          </p>
        )}
      </main>
    </div>
  );
}
