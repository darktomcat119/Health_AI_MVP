"use client";

import { cn } from "@/utils/cn";
import { RiskIndicator } from "./RiskIndicator";
import { formatSessionDate, truncateText } from "@/utils/formatters";
import type { Session } from "@/types";

interface SessionItemProps {
  /** Session data to display. */
  session: Session;
  /** Whether this session is currently active. */
  isActive: boolean;
  /** Callback when the session is clicked. */
  onClick: () => void;
}

/**
 * Individual session entry in the sidebar list.
 * Shows truncated title, timestamp, and risk indicator dot.
 */
export function SessionItem({ session, isActive, onClick }: SessionItemProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left px-3 py-2.5 rounded-lg transition-colors",
        "hover:bg-bg-chat focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50",
        isActive && "bg-bg-chat"
      )}
      type="button"
      aria-current={isActive ? "page" : undefined}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className={cn(
            "text-sm truncate",
            isActive ? "text-text-primary font-medium" : "text-text-secondary"
          )}>
            {truncateText(session.title, 35)}
          </p>
          <p className="text-xs text-text-secondary mt-0.5">
            {formatSessionDate(session.lastActivity)}
          </p>
        </div>
        <RiskIndicator level={session.riskLevel} className="mt-1.5" />
      </div>
    </button>
  );
}
