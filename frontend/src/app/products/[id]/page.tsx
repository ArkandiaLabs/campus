import { notFound, redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase-server";
import { getApiUrl } from "@/lib/api";
import Navbar from "@/components/Navbar";
import ContentList from "@/components/ContentList";
import SessionCard from "@/components/SessionCard";
import type { OfferingDetail } from "@/types";

async function getOffering(token: string, id: string): Promise<OfferingDetail | null> {
  const res = await fetch(`${getApiUrl()}/api/v1/catalog/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (res.status === 404) return null;
  if (!res.ok) return null;
  return res.json() as Promise<OfferingDetail>;
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

  const userName =
    (user.user_metadata?.full_name as string | undefined) ?? user.email ?? "";

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar userName={userName} />

      <main className="max-w-3xl mx-auto w-full px-space-md md:px-space-lg py-space-lg">
        <header className="mb-space-xl">
          <h1 className="font-h1 text-h1 text-foreground mb-space-md">
            {offering.title}
          </h1>
          {offering.description && (
            <p className="font-body text-body text-foreground">
              {offering.description}
            </p>
          )}
        </header>

        <section className="mb-space-xl">
          <h2 className="font-h2 text-h2 text-foreground mb-space-md">Sesiones</h2>
          {offering.sessions.length > 0 ? (
            <ol className="space-y-space-sm list-none p-0 m-0">
              {offering.sessions.map((s) => (
                <li key={s.id}>
                  <SessionCard offeringId={offering.id} session={s} />
                </li>
              ))}
            </ol>
          ) : (
            <p className="font-body text-body text-secondary">
              Aún no hay sesiones publicadas.
            </p>
          )}
        </section>

        {offering.general_resources.length > 0 && (
          <section>
            <h2 className="font-h2 text-h2 text-foreground mb-space-md">
              Recursos generales
            </h2>
            <ContentList contents={offering.general_resources} />
          </section>
        )}
      </main>
    </div>
  );
}
