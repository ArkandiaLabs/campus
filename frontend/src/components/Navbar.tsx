"use client";

import { useRouter } from "next/navigation";
import { createSupabaseBrowserClient } from "@/lib/supabase-browser";

interface NavbarProps {
  userName: string;
}

export default function Navbar({ userName }: NavbarProps) {
  const router = useRouter();

  async function handleLogout() {
    const supabase = createSupabaseBrowserClient();
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  return (
    <nav className="border-b border-secondary/20 bg-surface">
      <div className="max-w-5xl mx-auto px-md py-sm flex items-center justify-between">
        <span className="font-h2 text-h2 text-foreground">Arkandia</span>
        <div className="flex items-center gap-md">
          <span className="font-label text-label text-secondary hidden sm:block">
            {userName}
          </span>
          <button
            onClick={handleLogout}
            className="font-label text-label rounded-sm bg-primary text-on-primary px-md min-h-11 hover:bg-primary-hover active:bg-primary-active focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-focus-ring transition-colors"
          >
            Cerrar sesi&oacute;n
          </button>
        </div>
      </div>
    </nav>
  );
}