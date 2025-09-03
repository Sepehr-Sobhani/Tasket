import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import GitHubProvider from "next-auth/providers/github";
import { config } from "@/lib/config";

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      if (account?.provider === "google" || account?.provider === "github") {
        try {
          // Create or get user in our backend
          const response = await fetch(
            `${config.api.baseUrl}/api/v1/auth/oauth/user`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                provider: account.provider,
                provider_id: account.providerAccountId,
                email: user.email,
                name: user.name,
                avatar_url: user.image,
              }),
            }
          );

          if (!response.ok) {
            console.error("Failed to create/get user:", await response.text());
            return false;
          }

          const backendUser = await response.json();

          // Add backend user ID to the NextAuth user object
          user.id = backendUser.id;
          user.backendUserId = backendUser.id;

          return true;
        } catch (error) {
          console.error("Error in signIn callback:", error);
          return false;
        }
      }
      return true;
    },
    async jwt({ token, user, account }) {
      // Persist the backend user ID to the token right after signin
      if (user?.backendUserId) {
        token.backendUserId = user.backendUserId;
      }
      return token;
    },
    async session({ session, token }) {
      // Send backend user ID to the client
      if (token.backendUserId) {
        session.user.id = token.backendUserId as string;
      }
      return session;
    },
  },
  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
  },
  session: {
    strategy: "jwt",
  },
  secret: process.env.NEXTAUTH_SECRET,
});

export { handler as GET, handler as POST };
