"use client";

import { Sidebar } from "@/components/sidebar/Sidebar";
import { Header } from "@/components/layout/Header";
import { MobileNav } from "@/components/layout/MobileNav";
import { useUIStore } from "@/stores/uiStore";
import { cn } from "@/utils/cn";
import { SIDEBAR_WIDTH } from "@/utils/constants";

interface ChatLayoutProps {
  children: React.ReactNode;
}

/**
 * Chat layout with sidebar and header.
 * Manages responsive behavior: persistent sidebar on desktop,
 * drawer sidebar on mobile.
 */
export default function ChatLayout({ children }: ChatLayoutProps) {
  const sidebarOpen = useUIStore((state) => state.sidebarOpen);

  return (
    <div className="h-screen-safe flex flex-col bg-bg-primary">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        {/* Desktop sidebar */}
        <div
          className={cn(
            "hidden lg:block flex-shrink-0 border-r border-border transition-all duration-300",
            sidebarOpen ? "w-0 overflow-hidden" : ""
          )}
          style={!sidebarOpen ? { width: `${SIDEBAR_WIDTH}px` } : undefined}
        >
          <Sidebar />
        </div>

        {/* Mobile sidebar overlay */}
        {sidebarOpen && (
          <>
            <div
              className="lg:hidden fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
              onClick={() => useUIStore.getState().setSidebarOpen(false)}
              role="button"
              tabIndex={0}
              aria-label="Close sidebar"
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  useUIStore.getState().setSidebarOpen(false);
                }
              }}
            />
            <div className="lg:hidden fixed inset-y-0 left-0 z-50 w-[280px] animate-slide-down">
              <Sidebar />
            </div>
          </>
        )}

        {/* Main content */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {children}
        </main>
      </div>

      {/* Mobile bottom nav */}
      <div className="lg:hidden">
        <MobileNav />
      </div>
    </div>
  );
}
