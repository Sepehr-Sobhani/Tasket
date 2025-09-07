declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
    };
  }

  interface _User {
    id: string;
    backendUserId?: string;
  }
}

declare module "next-auth/jwt" {
  interface _JWT {
    backendUserId?: string;
  }
}
