export const config = {
  // Environment
  env: process.env.NODE_ENV || "development",

  // App Configuration
  app: {
    name: process.env.NEXT_PUBLIC_APP_NAME || "Flowmate",
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

export type Config = typeof config;
