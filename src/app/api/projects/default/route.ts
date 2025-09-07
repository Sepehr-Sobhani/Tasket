import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { prisma } from "@/lib/prisma";
import { authOptions } from "@/lib/auth-options";

async function getCurrentUser() {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return null;
  }

  return await prisma.user.findUnique({
    where: { id: session.user.id },
  });
}

export async function GET(_request: NextRequest) {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const project = await prisma.project.findFirst({
      where: {
        ownerId: user.id,
        isDefault: true,
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
    });

    if (!project) {
      return NextResponse.json(
        { error: "No default project found" },
        { status: 404 }
      );
    }

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
    console.error("Get default project error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
