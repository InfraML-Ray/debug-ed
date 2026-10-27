import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Debug Ed · Boilerplate",
  description: "Project structure for the Debug Ed LMS.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
