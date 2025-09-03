"use client";

import { signIn } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Github, Mail } from "lucide-react";
import { ThemeToggle } from "@/components/ui/theme-toggle";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-primary/20">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center shadow-sm">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <span className="text-lg font-semibold text-primary">Tasket</span>
          </div>
          <ThemeToggle />
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6 text-primary">
              Streamline Your Project Management
            </h1>
            <p className="text-xl text-muted-foreground mb-20 max-w-3xl mx-auto leading-relaxed">
              Organize tasks, track progress, and collaborate with your team.
              Tasket makes project management simple and efficient.
            </p>

            {/* OAuth Buttons */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center max-w-lg mx-auto">
              <Button
                variant="outline"
                size="lg"
                className="h-14 px-8 text-base font-bold flex-1 text-primary transition-all duration-200"
                onClick={() => signIn("github", { callbackUrl: "/projects" })}
              >
                <Github className="mr-3 h-5 w-5" />
                GitHub
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="h-14 px-8 text-base font-bold flex-1 text-primary transition-all duration-200"
                onClick={() => signIn("google", { callbackUrl: "/projects" })}
              >
                <Mail className="mr-3 h-5 w-5" />
                Google
              </Button>
            </div>
          </div>

          {/* Features Section */}
          <div className="mt-40 grid md:grid-cols-3 gap-8 lg:gap-12">
            <div className="text-center group hover:scale-105 transition-transform duration-200 p-6 rounded-xl border border-border/50 hover:border-primary/20 hover:shadow-lg">
              <div className="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:bg-primary/20 transition-colors">
                <svg
                  className="w-8 h-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-3 text-primary">
                Task Management
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                Create, organize, and track tasks with ease. Set priorities and
                assign work to team members.
              </p>
            </div>

            <div className="text-center group hover:scale-105 transition-transform duration-200 p-6 rounded-xl border border-border/50 hover:border-primary/20 hover:shadow-lg">
              <div className="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:bg-primary/20 transition-colors">
                <svg
                  className="w-8 h-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-3 text-primary">
                Team Collaboration
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                Work together seamlessly. Share projects, assign tasks, and keep
                everyone in sync.
              </p>
            </div>

            <div className="text-center group hover:scale-105 transition-transform duration-200 p-6 rounded-xl border border-border/50 hover:border-primary/20 hover:shadow-lg">
              <div className="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:bg-primary/20 transition-colors">
                <svg
                  className="w-8 h-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-3 text-primary">
                Progress Tracking
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                Monitor project progress with real-time updates and detailed
                analytics.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
