import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Debug Ed · Teacher workspace",
  description:
    "A shared foundation for curriculum, thoughtful lesson planning, and a teaching companion.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
