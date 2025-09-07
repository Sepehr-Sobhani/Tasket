import { z } from "zod";

export const projectCreateSchema = z.object({
  name: z
    .string()
    .min(1, "Project name is required")
    .max(100, "Project name must be less than 100 characters"),
  description: z
    .string()
    .max(500, "Description must be less than 500 characters")
    .optional(),
  visibility: z.enum(["public", "private"]).default("private"),
});

export const projectUpdateSchema = z.object({
  name: z
    .string()
    .min(1, "Project name is required")
    .max(100, "Project name must be less than 100 characters")
    .optional(),
  description: z
    .string()
    .max(500, "Description must be less than 500 characters")
    .optional(),
  visibility: z.enum(["public", "private"]).optional(),
  isActive: z.boolean().optional(),
});

export const projectMemberSchema = z.object({
  userId: z.string().cuid(),
  role: z.enum(["OWNER", "ADMIN", "MEMBER"]).default("MEMBER"),
});

export type ProjectCreateInput = z.infer<typeof projectCreateSchema>;
export type ProjectUpdateInput = z.infer<typeof projectUpdateSchema>;
export type ProjectMemberInput = z.infer<typeof projectMemberSchema>;
