import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Low Fare Calendar | Cheap Ticket Finder",
  description: "See the cheapest total price for every day of the month.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
