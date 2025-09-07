import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { prisma } from "@/lib/prisma";
import { authOptions } from "@/lib/auth-options";

async function getCurrentUser() {
  const session = await getServerSession(authOptions);
  // @ts-ignore - NextAuth session type compatibility
  if (!session?.user?.id) {
    return null;
  }

  return await prisma.user.findUnique({
    // @ts-ignore - NextAuth session type compatibility
    where: { id: session.user.id },
  });
}

export async function GET(_request: NextRequest) {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Get user's projects (owned or member of)
    const userProjects = await prisma.project.findMany({
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
        _count: {
          select: { members: true },
        },
      },
    });

    // Calculate stats
    const totalProjects = userProjects.length;
    const activeProjects = userProjects.filter(
      (project) => project.isActive
    ).length;

    // Get unique team members across all projects
    const uniqueTeamMembers = await prisma.projectMember.findMany({
      where: {
        project: {
          OR: [
            { ownerId: user.id },
            {
              members: {
                some: { userId: user.id },
              },
            },
          ],
        },
      },
      select: {
        userId: true,
      },
      distinct: ["userId"],
    });

    const stats = {
      total_projects: totalProjects,
      unique_team_members: uniqueTeamMembers.length,
      active_projects: activeProjects,
    };

    return NextResponse.json(stats);
  } catch (error) {
    console.error("Get dashboard stats error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
