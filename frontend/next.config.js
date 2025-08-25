/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ["avatars.githubusercontent.com", "localhost"],
  },
  // Environment variables are now handled by the config utility
  // No need to duplicate them here
};

module.exports = nextConfig;
