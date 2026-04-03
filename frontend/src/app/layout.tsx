import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Arkandia Campus",
  description: "Tu plataforma de aprendizaje",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="h-full">
      <body className="min-h-full bg-white text-gray-900 antialiased">{children}</body>
    </html>
  );
}
