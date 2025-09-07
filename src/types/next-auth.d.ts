declare module "next-auth" {
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
