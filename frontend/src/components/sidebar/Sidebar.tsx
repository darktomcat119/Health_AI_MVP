"use client";

import { Plus, Phone } from "lucide-react";
import { cn } from "@/utils/cn";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { SessionItem } from "./SessionItem";
import { useSession } from "@/hooks/useSession";
import { useUIStore } from "@/stores/uiStore";

/**
 * Sidebar with session list and controls.
 * Desktop: persistent left panel. Mobile: drawer overlay.
 */
export function Sidebar() {
  const { sessions, activeSessionId, createNewSession, switchSession } = useSession();
  const showCrisisBanner = useUIStore((state) => state.showCrisisBanner);
  const setSidebarOpen = useUIStore((state) => state.setSidebarOpen);

  const handleNewChat = () => {
    createNewSession();
    setSidebarOpen(false);
  };

  const handleSessionClick = (sessionId: string) => {
    switchSession(sessionId);
    setSidebarOpen(false);
  };

  return (
    <div className="h-full flex flex-col bg-bg-secondary">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-text-primary">Conversations</h2>
        </div>
        <button
          onClick={handleNewChat}
          className={cn(
            "w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg",
            "border border-border text-sm text-text-primary",
            "hover:bg-bg-chat transition-colors"
          )}
          type="button"
        >
          <Plus size={16} />
          New Chat
        </button>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {sessions.length === 0 ? (
          <p className="text-xs text-text-secondary text-center py-8 px-4">
            No conversations yet. Start a new chat to begin.
          </p>
        ) : (
          sessions.map((session) => (
            <SessionItem
              key={session.id}
              session={session}
              isActive={session.id === activeSessionId}
              onClick={() => handleSessionClick(session.id)}
            />
          ))
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-border space-y-2">
        <button
          onClick={showCrisisBanner}
          className={cn(
            "w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm",
            "text-crisis-text bg-crisis-bg/50 hover:bg-crisis-bg transition-colors"
          )}
          type="button"
        >
          <Phone size={14} />
          Need help now?
        </button>
        <div className="flex items-center justify-between">
          <ThemeToggle />
          <span className="text-xs text-text-secondary">v0.1.0</span>
        </div>
      </div>
    </div>
  );
}
