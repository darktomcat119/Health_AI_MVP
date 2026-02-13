"use client";

import { Menu, ShieldCheck } from "lucide-react";
import { useUIStore } from "@/stores/uiStore";
import { useChatStore } from "@/stores/chatStore";
import { RiskIndicator } from "@/components/sidebar/RiskIndicator";
import { cn } from "@/utils/cn";

/**
 * Top header bar with logo, session risk indicator, and controls.
 */
export function Header() {
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);
  const activeSessionId = useChatStore((state) => state.activeSessionId);
  const sessions = useChatStore((state) => state.sessions);

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  return (
    <header className="flex items-center justify-between px-4 h-14 border-b border-border bg-bg-secondary flex-shrink-0">
      <div className="flex items-center gap-3">
        {/* Mobile hamburger */}
        <button
          onClick={toggleSidebar}
          className="lg:hidden p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-chat transition-colors"
          aria-label="Toggle sidebar"
          type="button"
        >
          <Menu size={20} />
        </button>

        {/* Logo */}
        <div className="flex items-center gap-2">
          <ShieldCheck size={22} className="text-accent" />
          <span className="text-sm font-semibold text-text-primary hidden sm:inline">
            Mental Health Support
          </span>
        </div>
      </div>

      {/* Session risk indicator */}
      <div className="flex items-center gap-3">
        {activeSession && (
          <div className="flex items-center gap-2">
            <RiskIndicator level={activeSession.riskLevel} size="md" />
            <span className="text-xs text-text-secondary hidden sm:inline">
              Session active
            </span>
          </div>
        )}
      </div>
    </header>
  );
}
