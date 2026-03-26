/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return process.env.NODE_ENV === "development"
      ? [
          { source: "/api/download", destination: "http://localhost:3002/download" },
          { source: "/api/download-batch", destination: "http://localhost:3002/download-batch" },
          { source: "/api/info", destination: "http://localhost:3002/info" },
        ]
      : [];
  },
};

module.exports = nextConfig;
