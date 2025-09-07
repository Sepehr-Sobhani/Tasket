import NextAuth from "next-auth";
import { authOptions } from "@/lib/auth-options";

// @ts-ignore - NextAuth v4 type compatibility issues
const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
