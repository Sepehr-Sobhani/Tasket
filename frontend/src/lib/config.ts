export const config = {
  // Environment
  env: process.env.NODE_ENV || "development",

  // API Configuration
  api: {
    baseUrl: getApiBaseUrl(),
  },

  // App Configuration
  app: {
    name: process.env.NEXT_PUBLIC_APP_NAME || "Tasket",
    description:
      process.env.NEXT_PUBLIC_APP_DESCRIPTION ||
      "Collaborative Agile Project Management",
  },

  // OAuth Configuration
  oauth: {
    github: {
      clientId: process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID,
      redirectUri: process.env.NEXT_PUBLIC_GITHUB_REDIRECT_URI,
    },
  },
} as const;

function getApiBaseUrl(): string {
  // Read from environment variable
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  if (!apiUrl) {
    throw new Error("NEXT_PUBLIC_API_URL environment variable is required");
  }

  return apiUrl;
}

export type Config = typeof config;
