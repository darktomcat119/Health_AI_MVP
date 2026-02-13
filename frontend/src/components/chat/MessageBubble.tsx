"use client";

import { motion } from "framer-motion";
import { cn } from "@/utils/cn";
import { formatMessageTime } from "@/utils/formatters";
import { RISK_COLOR_MAP, RISK_ANIMATION_MAP } from "@/utils/constants";
import { Avatar } from "@/components/common/Avatar";
import type { Message } from "@/types";

interface MessageBubbleProps {
  message: Message;
}

/**
 * A single chat message bubble.
 *
 * - User messages are right-aligned with the user-bubble theme colors.
 * - Assistant messages are left-aligned with the bot-bubble theme colors
 *   and preceded by an Avatar component.
 * - Triage messages display a small colored risk-level dot beneath the bubble.
 * - Timestamp is displayed via the title attribute on hover.
 */
export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const timeString = formatMessageTime(message.timestamp);

  const riskColor =
    message.riskLevel != null ? RISK_COLOR_MAP[message.riskLevel] : undefined;
  const riskAnimation =
    message.riskLevel != null
      ? RISK_ANIMATION_MAP[message.riskLevel]
      : undefined;
  const showRiskDot =
    message.triageActivated === true && riskColor != null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={cn(
        "flex gap-3 px-4 sm:px-6",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar for assistant messages */}
      {!isUser && <Avatar />}

      {/* Bubble + optional risk dot */}
      <div
        className={cn(
          "flex flex-col",
          isUser ? "items-end" : "items-start",
          "max-w-[75%] sm:max-w-[65%]"
        )}
      >
        <div
          title={timeString}
          className={cn(
            "whitespace-pre-wrap break-words rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
            isUser
              ? "rounded-br-md bg-bg-user-bubble text-text-user-bubble"
              : "rounded-bl-md bg-bg-bot-bubble text-text-primary"
          )}
        >
          {message.content}
        </div>

        {/* Risk level dot for triage messages */}
        {showRiskDot && (
          <div className="mt-1 flex items-center gap-1.5">
            <span
              className={cn(
                "inline-block h-2 w-2 rounded-full",
                riskColor,
                riskAnimation
              )}
              aria-label={`Risk level: ${message.riskLevel ?? "unknown"}`}
            />
            <span className="text-[10px] text-text-secondary capitalize">
              {message.riskLevel}
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
