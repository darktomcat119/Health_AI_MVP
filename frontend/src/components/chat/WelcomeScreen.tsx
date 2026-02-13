"use client";

import { motion } from "framer-motion";
import { ShieldCheck } from "lucide-react";
import { cn } from "@/utils/cn";

interface WelcomeScreenProps {
  onSuggestionClick: (suggestion: string) => void;
}

const SUGGESTIONS = [
  "I've been feeling stressed lately",
  "I need someone to talk to",
  "I want to do a daily check-in",
  "How does this work?",
] as const;

/**
 * Welcome screen displayed when the conversation is empty.
 *
 * Provides a warm greeting, the bot avatar (ShieldCheck icon with a gentle
 * pulse), and four clickable suggestion chips so the user can start a
 * conversation without having to think of an opening message.
 */
export function WelcomeScreen({ onSuggestionClick }: WelcomeScreenProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 text-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="flex max-w-md flex-col items-center"
      >
        {/* Bot avatar */}
        <motion.div
          animate={{ scale: [1, 1.05, 1] }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="mb-6"
        >
          <ShieldCheck className="h-16 w-16 text-accent" strokeWidth={1.5} />
        </motion.div>

        {/* Heading */}
        <h2 className="mb-3 text-2xl font-semibold text-text-primary">
          Hi, I&apos;m here to listen
        </h2>

        {/* Subtext */}
        <p className="mb-8 text-sm leading-relaxed text-text-secondary">
          You can share whatever is on your mind. This is a safe space.
        </p>

        {/* Suggestion chips */}
        <div className="mb-8 flex flex-wrap items-center justify-center gap-2">
          {SUGGESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => onSuggestionClick(suggestion)}
              className={cn(
                "rounded-full border border-border px-4 py-2",
                "text-sm text-text-primary",
                "transition-colors hover:bg-accent/10",
                "focus-visible:outline-2 focus-visible:outline-accent"
              )}
            >
              {suggestion}
            </button>
          ))}
        </div>

        {/* Privacy note */}
        <p className="text-xs text-text-secondary">
          Your conversations are private and encrypted.
        </p>
      </motion.div>
    </div>
  );
}
