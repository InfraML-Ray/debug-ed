"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getUserManager } from "@/lib/auth";

let callback: Promise<unknown> | undefined;

export default function Callback() {
  const [error, setError] = useState("");
  useEffect(() => {
    callback ??= getUserManager().signinRedirectCallback();
    callback
      .then(() => window.location.replace("/"))
      .catch(() => setError("Sign-in failed. Please return and try again."));
  }, []);
  return (
    <main className="auth-card">
      <h1>{error || "Completing school sign-in…"}</h1>
      <Link href="/">Return to workspace</Link>
    </main>
  );
}
