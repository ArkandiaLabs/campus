import { notFound, redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase-server";
import { getApiUrl } from "@/lib/api";
import Navbar from "@/components/Navbar";
import BackLink from "@/components/BackLink";
import VimeoPlayer from "@/components/VimeoPlayer";
import ContentList from "@/components/ContentList";
import { formatSessionMeta } from "@/lib/format";
import type { SessionDetail } from "@/types";

async function getSession(
  token: string,
  sessionId: string,
): Promise<SessionDetail | null> {
  const res = await fetch(`${getApiUrl()}/api/v1/catalog/sessions/${sessionId}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (res.status === 404) return null;
  if (!res.ok) return null;
  return res.json() as Promise<SessionDetail>;
}

interface SessionPageProps {
  params: Promise<{ id: string; sessionId: string }>;
}

export default async function SessionPage({ params }: SessionPageProps) {
  const { id, sessionId } = await params;

  const supabase = await createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const {
    data: { session: authSession },
  } = await supabase.auth.getSession();
  if (!authSession) redirect("/login");

  const sessionDetail = await getSession(authSession.access_token, sessionId);
  if (!sessionDetail) notFound();

  const userName =
    (user.user_metadata?.full_name as string | undefined) ?? user.email ?? "";

  const videoContent = sessionDetail.contents.find(
    (c) => c.content_type === "video",
  );
  const otherContents = sessionDetail.contents.filter(
    (c) => c.content_type !== "video",
  );
  const meta = formatSessionMeta(
    sessionDetail.scheduled_at,
    sessionDetail.duration_minutes,
  );

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar userName={userName} />

      <main className="mx-auto w-full max-w-5xl px-space-md md:px-space-lg py-space-lg">
        <div className="max-w-3xl mx-auto">
          <BackLink href={`/products/${id}`}>Volver al workshop</BackLink>

          <header className="mt-space-md mb-space-lg">
            <h1 className="font-h1 text-h1 text-foreground mb-space-xs">
              {sessionDetail.title}
            </h1>
            <p className="font-label text-label text-secondary">{meta}</p>
          </header>
        </div>

        <div className="mb-space-lg">
          <VimeoPlayer
            url={videoContent?.content_url ?? null}
            title={sessionDetail.title}
          />
        </div>

        <div className="max-w-3xl mx-auto">
          {sessionDetail.description && (
            <p className="font-body text-body text-foreground mb-space-xl">
              {sessionDetail.description}
            </p>
          )}

          {otherContents.length > 0 && (
            <section>
              <h2 className="font-h2 text-h2 text-foreground mb-space-md">
                Recursos de la sesión
              </h2>
              <ContentList contents={otherContents} />
            </section>
          )}
        </div>
      </main>
    </div>
  );
}
