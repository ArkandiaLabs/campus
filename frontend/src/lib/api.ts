import { createSupabaseBrowserClient } from "@/lib/supabase-browser";
import type { OfferingDetail, UserOffering } from "@/types";

export function getApiUrl(): string {
  return (
    process.env.API_INTERNAL_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    "http://localhost:8000"
  );
}

const API_URL = getApiUrl();

class ApiClient {
  private async getToken(): Promise<string | null> {
    const supabase = createSupabaseBrowserClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();
    return session?.access_token ?? null;
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const token = await this.getToken();

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    };

    const response = await fetch(`${API_URL}${path}`, { ...init, headers });

    if (response.status === 401) {
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }

    if (!response.ok) {
      const body = (await response.json().catch(() => ({}))) as { detail?: string };
      throw new Error(body.detail ?? `API error ${response.status}`);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json() as Promise<T>;
  }

  async getCatalog(): Promise<UserOffering[]> {
    return this.request<UserOffering[]>("/api/v1/catalog");
  }

  async getOffering(id: string): Promise<OfferingDetail> {
    return this.request<OfferingDetail>(`/api/v1/catalog/${id}`);
  }
}

export const api = new ApiClient();
