/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['api.dicebear.com'], // For avatar placeholder images
  },
}

module.exports = nextConfig