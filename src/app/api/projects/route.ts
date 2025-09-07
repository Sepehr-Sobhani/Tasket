import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { prisma } from "@/lib/prisma";
import { projectCreateSchema } from "@/lib/validations/project";
import { authOptions } from "@/lib/auth-options";

async function getCurrentUser(request: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return null;
  }

  return await prisma.user.findUnique({
    where: { id: session.user.id },
  });
}

export async function GET(request: NextRequest) {
  try {
    const user = await getCurrentUser(request);
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const url = new URL(request.url);
    const skip = parseInt(url.searchParams.get("skip") || "0");
    const limit = parseInt(url.searchParams.get("limit") || "10");

    const projects = await prisma.project.findMany({
      where: {
        OR: [
          { ownerId: user.id },
          {
            members: {
              some: { userId: user.id },
            },
          },
        ],
      },
      include: {
        owner: {
          select: {
            id: true,
            username: true,
            fullName: true,
            avatarUrl: true,
          },
        },
        _count: {
          select: { members: true },
        },
      },
      skip,
      take: limit,
      orderBy: { createdAt: "desc" },
    });

    const formattedProjects = projects.map((project) => ({
      id: project.id,
      name: project.name,
      description: project.description,
      visibility: project.visibility.toLowerCase(),
      isActive: project.isActive,
      isDefault: project.isDefault,
      githubRepoId: project.githubRepoId,
      githubRepoName: project.githubRepoName,
      githubRepoOwner: project.githubRepoOwner,
      createdAt: project.createdAt.toISOString(),
      updatedAt: project.updatedAt?.toISOString() || null,
      memberCount: project._count.members,
    }));

    return NextResponse.json(formattedProjects);
  } catch (error) {
    console.error("Get projects error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const user = await getCurrentUser(request);
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const validatedData = projectCreateSchema.parse(body);

    const project = await prisma.project.create({
      data: {
        name: validatedData.name,
        description: validatedData.description,
        visibility: validatedData.visibility.toUpperCase() as
          | "PUBLIC"
          | "PRIVATE",
        ownerId: user.id,
        members: {
          create: {
            userId: user.id,
            role: "OWNER",
          },
        },
      },
      include: {
        _count: {
          select: { members: true },
        },
      },
    });

    const formattedProject = {
      id: project.id,
      name: project.name,
      description: project.description,
      visibility: project.visibility.toLowerCase(),
      isActive: project.isActive,
      isDefault: project.isDefault,
      githubRepoId: project.githubRepoId,
      githubRepoName: project.githubRepoName,
      githubRepoOwner: project.githubRepoOwner,
      createdAt: project.createdAt.toISOString(),
      updatedAt: project.updatedAt?.toISOString() || null,
      memberCount: project._count.members,
    };

    return NextResponse.json(formattedProject);
  } catch (error) {
    if (error instanceof Error && error.name === "ZodError") {
      return NextResponse.json(
        { error: "Validation error", details: error.message },
        { status: 422 }
      );
    }

    console.error("Create project error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
