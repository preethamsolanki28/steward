"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

// Static export has no server redirects, so / -> /chat is a client-side replace (docs/03 §6).
export default function Home() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/chat");
  }, [router]);
  return null;
}
