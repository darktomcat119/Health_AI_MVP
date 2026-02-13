"use client";

import { cn } from "@/utils/cn";
import type { RiskLevel } from "@/types";
import { RISK_COLOR_MAP, RISK_ANIMATION_MAP } from "@/utils/constants";

interface RiskIndicatorProps {
  /** Risk level to display. */
  level: RiskLevel;
  /** Size variant. */
  size?: "sm" | "md";
  /** Additional CSS classes. */
  className?: string;
}

const SIZE_MAP = {
  sm: "h-2 w-2",
  md: "h-2.5 w-2.5",
} as const;

/**
 * Colored dot indicator for risk level.
 * Static for low, pulsing for medium/high, ring pulse for critical.
 */
export function RiskIndicator({ level, size = "sm", className }: RiskIndicatorProps) {
  return (
    <span
      className={cn(
        "inline-block rounded-full flex-shrink-0",
        RISK_COLOR_MAP[level],
        RISK_ANIMATION_MAP[level],
        SIZE_MAP[size],
        level === "critical" && "ring-2 ring-red-500/30",
        className
      )}
      role="status"
      aria-label={`Risk level: ${level}`}
    />
  );
}
