"use client";

import { useRouter } from "next/navigation";
import { createSupabaseBrowserClient } from "@/lib/supabase";

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
    <nav className="border-b border-gray-200 bg-white">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <span className="text-lg font-bold text-gray-900 tracking-tight">Arkandia</span>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600 hidden sm:block">{userName}</span>
          <button
            onClick={handleLogout}
            className="text-sm text-blue-600 hover:underline"
          >
            Cerrar sesion
          </button>
        </div>
      </div>
    </nav>
  );
}
