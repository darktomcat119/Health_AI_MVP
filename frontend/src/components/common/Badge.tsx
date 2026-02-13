"use client";

import { cn } from "@/utils/cn";

type BadgeVariant = "default" | "success" | "warning" | "danger" | "info";

interface BadgeProps {
  /** Badge content. */
  children: React.ReactNode;
  /** Visual style variant. */
  variant?: BadgeVariant;
  /** Additional CSS classes. */
  className?: string;
}

const VARIANT_CLASSES: Record<BadgeVariant, string> = {
  default: "bg-bg-chat text-text-secondary",
  success: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  warning: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
  danger: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  info: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
};

/**
 * Status badge component for labels and indicators.
 */
export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
        VARIANT_CLASSES[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
