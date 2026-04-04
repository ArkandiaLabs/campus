import { createServerClient, type CookieOptions } from "@supabase/ssr";
import { cookies } from "next/headers";

export async function createSupabaseServerClient() {
  const publicUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const internalUrl = process.env.SUPABASE_INTERNAL_URL ?? publicUrl;
  const cookieStore = await cookies();
  return createServerClient(
    publicUrl,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      global: {
        fetch: (input, init) => {
          const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
          return fetch(url.replace(publicUrl, internalUrl), init);
        },
      },
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value;
        },
        set(name: string, value: string, options: CookieOptions) {
          cookieStore.set({ name, value, ...options });
        },
        remove(name: string, options: CookieOptions) {
          cookieStore.set({ name, value: "", ...options });
        },
      },
    }
  );
}
