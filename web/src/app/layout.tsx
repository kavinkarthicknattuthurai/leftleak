import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: 'swap',
});

export const metadata: Metadata = {
  title: "LeftLeak - See what they're really saying",
  description: "Understand progressive perspectives from Bluesky with sources.",
  keywords: ["progressive", "bluesky", "social media", "research"],
  openGraph: {
    title: "LeftLeak - What the Left Thinks",
    description: "Concise summaries with sources.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
