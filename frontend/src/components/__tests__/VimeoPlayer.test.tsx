import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import VimeoPlayer from "@/components/VimeoPlayer";

describe("VimeoPlayer", () => {
  it("embeds iframe for vimeo.com/{id}", () => {
    const { container } = render(
      <VimeoPlayer url="https://vimeo.com/100000001" title="Sesión 1" />,
    );
    const iframe = container.querySelector("iframe");
    expect(iframe).not.toBeNull();
    expect(iframe?.getAttribute("src")).toBe(
      "https://player.vimeo.com/video/100000001",
    );
    expect(iframe?.getAttribute("title")).toBe("Grabación: Sesión 1");
  });

  it("embeds iframe for player.vimeo.com/video/{id}", () => {
    const { container } = render(
      <VimeoPlayer
        url="https://player.vimeo.com/video/200000002"
        title="Sesión 2"
      />,
    );
    const iframe = container.querySelector("iframe");
    expect(iframe?.getAttribute("src")).toBe(
      "https://player.vimeo.com/video/200000002",
    );
  });

  it("renders fallback when URL has no numeric id", () => {
    const { container } = render(
      <VimeoPlayer
        url="https://vimeo.com/placeholder/sesion-1"
        title="Sesión 1"
      />,
    );
    expect(container.querySelector("iframe")).toBeNull();
    expect(screen.getByText("Grabación no disponible aún")).toBeDefined();
  });

  it("renders fallback for null URL", () => {
    const { container } = render(<VimeoPlayer url={null} title="Sesión 1" />);
    expect(container.querySelector("iframe")).toBeNull();
    expect(screen.getByText("Grabación no disponible aún")).toBeDefined();
  });

  it("renders fallback for empty URL", () => {
    const { container } = render(<VimeoPlayer url="" title="Sesión 1" />);
    expect(container.querySelector("iframe")).toBeNull();
    expect(screen.getByText("Grabación no disponible aún")).toBeDefined();
  });
});
