"use client";

import { Sidebar } from "./Sidebar";

interface AppLayoutProps {
  children: React.ReactNode;
  user: any;
  onLogout: () => void;
}

export function AppLayout({ children, user, onLogout }: AppLayoutProps) {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar user={user} onLogout={onLogout} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
