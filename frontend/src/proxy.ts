import { createServerClient, type CookieOptions } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function proxy(request: NextRequest) {
  let response = NextResponse.next({
    request: { headers: request.headers },
  });

  const publicUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const internalUrl = process.env.SUPABASE_INTERNAL_URL ?? publicUrl;

  const supabase = createServerClient(
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
          return request.cookies.get(name)?.value;
        },
        set(name: string, value: string, options: CookieOptions) {
          request.cookies.set({ name, value, ...options });
          response = NextResponse.next({
            request: { headers: request.headers },
          });
          response.cookies.set({ name, value, ...options });
        },
        remove(name: string, options: CookieOptions) {
          request.cookies.set({ name, value: "", ...options });
          response = NextResponse.next({
            request: { headers: request.headers },
          });
          response.cookies.set({ name, value: "", ...options });
        },
      },
    }
  );

  const {
    data: { user },
  } = await supabase.auth.getUser();

  const { pathname } = request.nextUrl;

  // Protected routes — redirect to /login if not authenticated
  if ((pathname.startsWith("/dashboard") || pathname.startsWith("/products")) && !user) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Auth routes — redirect to /dashboard if already authenticated
  if ((pathname === "/login" || pathname === "/register") && user) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return response;
}

export const config = {
  matcher: ["/dashboard/:path*", "/products/:path*", "/login", "/register"],
};
