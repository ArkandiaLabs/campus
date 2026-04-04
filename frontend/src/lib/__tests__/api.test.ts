import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock supabase before importing api
vi.mock("@/lib/supabase-browser", () => ({
  createSupabaseBrowserClient: () => ({
    auth: {
      getSession: () =>
        Promise.resolve({
          data: { session: { access_token: "test-token" } },
        }),
    },
  }),
}));

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Avoid window.location redirect errors in jsdom
Object.defineProperty(window, "location", {
  value: { href: "" },
  writable: true,
});

describe("ApiClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("getCatalog attaches Bearer token and returns data", async () => {
    const mockOfferings = [{ id: "1", title: "Workshop" }];
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockOfferings),
    });

    const { api } = await import("@/lib/api");
    const result = await api.getCatalog();

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/catalog"),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
        }),
      })
    );
    expect(result).toEqual(mockOfferings);
  });

  it("redirects to /login on 401", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: () => Promise.resolve({}),
    });

    const { api } = await import("@/lib/api");
    await expect(api.getCatalog()).rejects.toThrow("Unauthorized");
    expect(window.location.href).toBe("/login");
  });
});
