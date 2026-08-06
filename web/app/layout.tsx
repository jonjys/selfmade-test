import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Går er kassa att slutföra utan mus?",
  description:
    "Sedan juni 2025 omfattas e-handel av tillgänglighetslagen och PTS har " +
    "inlett tillsyn. Kostnadsfri skanning visar var det brister i er kassa.",
  openGraph: {
    type: "website",
    locale: "sv_SE",
    title: "Går er kassa att slutföra utan mus?",
    description:
      "Sedan juni 2025 omfattas e-handel av tillgänglighetslagen och PTS " +
      "har inlett tillsyn. Kostnadsfri skanning visar var det brister.",
  },
  icons: {
    icon:
      "data:image/svg+xml," +
      encodeURIComponent(
        `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">` +
          `<rect width="32" height="32" rx="6" fill="#1f6f4a"/>` +
          `<rect x="7" y="9" width="18" height="14" rx="3" fill="none" ` +
          `stroke="#ffb020" stroke-width="3"/></svg>`,
      ),
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="sv">
      <body>
        <a
          href="#innehall"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:bg-blaeck focus:px-5 focus:py-3 focus:text-papper"
        >
          Hoppa till innehållet
        </a>
        <main id="innehall">{children}</main>
      </body>
    </html>
  );
}
