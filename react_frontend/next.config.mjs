/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: "export", // output st
  output: "standalone",
  reactStrictMode: true,
  images: {
    domains: ["localhost"],
  },
};

export default nextConfig;
