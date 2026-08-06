import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Statisk export. Sidan ska kunna ligga på vilken statisk värd som helst
  // och kan inte gå sönder av att en serverfunktion timear ut mitt i natten.
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true,
};

export default nextConfig;
