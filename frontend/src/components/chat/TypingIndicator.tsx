"use client";

import { Avatar } from "@/components/common/Avatar";

/**
 * Animated typing indicator with three bouncing dots.
 *
 * Displayed left-aligned alongside the bot Avatar while the assistant
 * response is being generated but no tokens have arrived yet. Each dot
 * uses the Tailwind `animate-bounce-dots` keyframe with a staggered
 * animation-delay to create the classic sequential bounce effect.
 */
export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 px-4 sm:px-6" role="status">
      <Avatar />

      <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-md bg-bg-bot-bubble px-4 py-3">
        <span
          className="h-2 w-2 rounded-full bg-text-secondary animate-bounce-dots"
          style={{ animationDelay: "0s" }}
        />
        <span
          className="h-2 w-2 rounded-full bg-text-secondary animate-bounce-dots"
          style={{ animationDelay: "0.15s" }}
        />
        <span
          className="h-2 w-2 rounded-full bg-text-secondary animate-bounce-dots"
          style={{ animationDelay: "0.3s" }}
        />
        <span className="sr-only">Assistant is typing</span>
      </div>
    </div>
  );
}
