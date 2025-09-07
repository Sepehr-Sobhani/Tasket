import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { prisma } from "@/lib/prisma";
import { projectUpdateSchema } from "@/lib/validations/project";
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

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const project = await prisma.project.findFirst({
      where: {
        id: params.id,
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
    });

    if (!project) {
      return NextResponse.json({ error: "Project not found" }, { status: 404 });
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
    console.error("Get project error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Check if user is owner or admin of the project
    const project = await prisma.project.findFirst({
      where: {
        id: params.id,
        OR: [
          { ownerId: user.id },
          {
            members: {
              some: {
                userId: user.id,
                role: { in: ["OWNER", "ADMIN"] },
              },
            },
          },
        ],
      },
    });

    if (!project) {
      return NextResponse.json(
        { error: "Project not found or insufficient permissions" },
        { status: 404 }
      );
    }

    const body = await request.json();
    const validatedData = projectUpdateSchema.parse(body);

    const updatedProject = await prisma.project.update({
      where: { id: params.id },
      data: {
        ...(validatedData.name && { name: validatedData.name }),
        ...(validatedData.description !== undefined && {
          description: validatedData.description,
        }),
        ...(validatedData.visibility && {
          visibility: validatedData.visibility.toUpperCase() as
            | "PUBLIC"
            | "PRIVATE",
        }),
        ...(validatedData.isActive !== undefined && {
          isActive: validatedData.isActive,
        }),
      },
      include: {
        _count: {
          select: { members: true },
        },
      },
    });

    const formattedProject = {
      id: updatedProject.id,
      name: updatedProject.name,
      description: updatedProject.description,
      visibility: updatedProject.visibility.toLowerCase(),
      isActive: updatedProject.isActive,
      isDefault: updatedProject.isDefault,
      githubRepoId: updatedProject.githubRepoId,
      githubRepoName: updatedProject.githubRepoName,
      githubRepoOwner: updatedProject.githubRepoOwner,
      createdAt: updatedProject.createdAt.toISOString(),
      updatedAt: updatedProject.updatedAt?.toISOString() || null,
      memberCount: updatedProject._count.members,
    };

    return NextResponse.json(formattedProject);
  } catch (error) {
    if (error instanceof Error && error.name === "ZodError") {
      return NextResponse.json(
        { error: "Validation error", details: error.message },
        { status: 422 }
      );
    }

    console.error("Update project error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Check if user is owner of the project
    const project = await prisma.project.findFirst({
      where: {
        id: params.id,
        ownerId: user.id,
      },
    });

    if (!project) {
      return NextResponse.json(
        { error: "Project not found or insufficient permissions" },
        { status: 404 }
      );
    }

    await prisma.project.delete({
      where: { id: params.id },
    });

    return NextResponse.json({ message: "Project deleted successfully" });
  } catch (error) {
    console.error("Delete project error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
