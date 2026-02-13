"use client";

import { motion } from "framer-motion";
import { cn } from "@/utils/cn";
import { Avatar } from "@/components/common/Avatar";

interface StreamingMessageProps {
  /** The currently accumulated streamed text content. */
  content: string;
  /** Whether the stream is still active (controls cursor visibility). */
  isStreaming: boolean;
}

/**
 * A bot message bubble that renders streamed content with a blinking cursor.
 *
 * - The cursor is visible while `isStreaming` is true, using the
 *   `animate-blink` animation defined in the Tailwind config.
 * - When streaming finishes, the cursor fades out via an opacity transition.
 * - Uses framer-motion `layout` for smooth height changes as content grows.
 */
export function StreamingMessage({
  content,
  isStreaming,
}: StreamingMessageProps) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className="flex items-start gap-3 px-4 sm:px-6"
    >
      <Avatar />

      <div className="max-w-[75%] sm:max-w-[65%]">
        <motion.div
          layout
          className="whitespace-pre-wrap break-words rounded-2xl rounded-bl-md bg-bg-bot-bubble px-4 py-2.5 text-sm leading-relaxed text-text-primary"
        >
          {content}
          <span
            className={cn(
              "inline-block w-0.5 h-[1.1em] align-middle ml-0.5 bg-accent rounded-full",
              isStreaming ? "animate-blink opacity-100" : "opacity-0",
              "transition-opacity duration-300 ease-in-out"
            )}
            aria-hidden="true"
          />
        </motion.div>
      </div>
    </motion.div>
  );
}
