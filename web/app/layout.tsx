import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bedelli MP3 İndirici",
  description: "Askeri temalı YouTube MP3 indirici",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
