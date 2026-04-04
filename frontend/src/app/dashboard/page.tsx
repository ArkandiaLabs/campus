import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase-server";
import Navbar from "@/components/Navbar";
import OfferingCard from "@/components/OfferingCard";
import type { UserOffering } from "@/types";

async function getCatalog(token: string): Promise<UserOffering[]> {
  const apiUrl = process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const res = await fetch(`${apiUrl}/api/v1/catalog`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!res.ok) return [];
  return res.json() as Promise<UserOffering[]>;
}

export default async function DashboardPage() {
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

  const offerings = session ? await getCatalog(session.access_token) : [];

  const firstName =
    (user.user_metadata?.full_name as string | undefined)?.split(" ")[0] ??
    user.email?.split("@")[0] ??
    "usuario";

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar userName={user.user_metadata?.full_name as string | undefined ?? user.email ?? ""} />

      <main className="max-w-5xl mx-auto w-full px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Hola, {firstName}</h1>

        {offerings.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-gray-500">
              Aun no tienes productos.{" "}
              <a
                href="https://arkandia.co"
                className="text-blue-600 hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                Visita arkandia.co
              </a>{" "}
              para ver nuestros workshops.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {offerings.map((offering) => (
              <OfferingCard key={offering.id} offering={offering} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
