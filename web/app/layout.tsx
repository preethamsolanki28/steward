import type { Metadata } from "next";
import { Geist } from "next/font/google";

import { AppShell } from "@/components/app-shell";
import { cn } from "@/lib/utils";
import "./globals.css";

// TODO(T0.7): replace Geist with Inter + JetBrains Mono via next/font (docs/03 §3).
const geist = Geist({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "Steward",
  description: "Your assistant, your clients, your receipts.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <body className="bg-background text-foreground antialiased">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
