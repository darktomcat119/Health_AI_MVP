"use client";

import { ShieldCheck, User } from "lucide-react";
import { cn } from "@/utils/cn";

interface AvatarProps {
  /** Whether this is a bot avatar (true) or user avatar (false). */
  isBot?: boolean;
  /** Size variant. */
  size?: "sm" | "md" | "lg";
  /** Additional CSS classes. */
  className?: string;
}

const SIZE_MAP = {
  sm: "h-7 w-7",
  md: "h-8 w-8",
  lg: "h-10 w-10",
} as const;

const ICON_SIZE_MAP = {
  sm: 14,
  md: 16,
  lg: 20,
} as const;

/**
 * Avatar component for user and bot message bubbles.
 * Bot uses a calming heart-shield icon; user shows a person icon.
 */
export function Avatar({ isBot = true, size = "md", className }: AvatarProps) {
  const Icon = isBot ? ShieldCheck : User;

  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-full flex-shrink-0",
        isBot
          ? "bg-accent/10 text-accent"
          : "bg-bg-user-bubble/10 text-bg-user-bubble",
        SIZE_MAP[size],
        className
      )}
      role="img"
      aria-label={isBot ? "Chatbot avatar" : "User avatar"}
    >
      <Icon size={ICON_SIZE_MAP[size]} />
    </div>
  );
}
