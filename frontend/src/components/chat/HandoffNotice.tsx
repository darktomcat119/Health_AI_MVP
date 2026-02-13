"use client";

import { motion } from "framer-motion";
import { cn } from "@/utils/cn";

/**
 * Professional handoff notice displayed as a full-width banner inside the
 * chat area above the input.
 *
 * Shows a calming teal-themed message informing the user that a human
 * professional is joining the conversation, along with an animated pulse
 * dot to convey an active connection in progress.
 */
export function HandoffNotice() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={cn(
        "mx-4 mb-3 rounded-xl p-4 sm:mx-6",
        "bg-teal-50 text-teal-800",
        "dark:bg-teal-900/30 dark:text-teal-200"
      )}
      role="status"
    >
      <div className="flex items-center gap-3">
        {/* Animated connecting pulse dot */}
        <span
          className="h-2 w-2 shrink-0 rounded-full bg-teal-500 animate-pulse"
          aria-hidden="true"
        />

        <div>
          <p className="text-sm font-semibold">
            A professional is joining your conversation
          </p>
          <p className="mt-0.5 text-xs opacity-80">
            They will see our conversation history so you won&apos;t have to
            repeat anything.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
