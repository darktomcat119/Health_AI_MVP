"use client";

import { useCallback, useRef, useState, type KeyboardEvent } from "react";
import { ArrowUp, Square } from "lucide-react";
import { cn } from "@/utils/cn";
import { useUIStore } from "@/stores/uiStore";
import {
  MAX_MESSAGE_LENGTH,
  SHOW_COUNTER_THRESHOLD,
} from "@/utils/constants";

interface ChatInputProps {
  /** Callback invoked with the trimmed message when the user submits. */
  onSend: (message: string) => void;
  /** Whether the assistant is currently streaming a response. */
  isStreaming: boolean;
  /** Callback to stop the active stream. */
  onStop: () => void;
}

/**
 * Chat input area with an auto-growing textarea, send/stop button,
 * character counter, and a persistent crisis help link.
 *
 * - Enter sends, Shift+Enter inserts a newline.
 * - Input is disabled during streaming; only the stop button remains active.
 * - Character counter appears when the user exceeds SHOW_COUNTER_THRESHOLD.
 * - A "Need help now?" link triggers the crisis banner via useUIStore.
 */
export function ChatInput({ onSend, isStreaming, onStop }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const showCrisisBanner = useUIStore((s) => s.showCrisisBanner);

  const charCount = value.length;
  const isOverLimit = charCount > MAX_MESSAGE_LENGTH;
  const showCounter = charCount > SHOW_COUNTER_THRESHOLD;
  const canSend = value.trim().length > 0 && !isOverLimit && !isStreaming;

  /**
   * Resize the textarea to fit its content, up to max-h defined in CSS.
   */
  const resizeTextarea = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }, []);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setValue(e.target.value);
      resizeTextarea();
    },
    [resizeTextarea]
  );

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (trimmed.length === 0 || isOverLimit || isStreaming) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, isOverLimit, isStreaming, onSend]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleButtonClick = useCallback(() => {
    if (isStreaming) {
      onStop();
    } else {
      handleSend();
    }
  }, [isStreaming, onStop, handleSend]);

  return (
    <div className="px-4 pb-3 pt-2 sm:px-6">
      {/* Input row */}
      <div
        className={cn(
          "flex items-end gap-2 rounded-xl border border-border bg-bg-secondary",
          "px-3 py-2 transition-all",
          "focus-within:ring-2 focus-within:ring-accent/50 focus-within:border-accent"
        )}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          disabled={isStreaming}
          placeholder="Type your message..."
          rows={1}
          aria-label="Message input"
          className={cn(
            "flex-1 resize-none bg-transparent text-sm leading-relaxed text-text-primary",
            "placeholder:text-text-secondary",
            "outline-none",
            "max-h-[6rem] overflow-y-auto",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        />

        {/* Send / Stop button */}
        <button
          type="button"
          onClick={handleButtonClick}
          disabled={!isStreaming && !canSend}
          aria-label={isStreaming ? "Stop generating" : "Send message"}
          className={cn(
            "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-colors",
            isStreaming
              ? "bg-red-500 text-white hover:bg-red-600"
              : canSend
                ? "bg-accent text-white hover:bg-accent/90"
                : "bg-bg-primary text-text-secondary cursor-not-allowed opacity-40"
          )}
        >
          {isStreaming ? (
            <Square className="h-3.5 w-3.5" fill="currentColor" />
          ) : (
            <ArrowUp className="h-4 w-4" />
          )}
        </button>
      </div>

      {/* Character counter */}
      <div className="mt-1 flex items-center justify-between px-1">
        <div />
        {showCounter && (
          <span
            className={cn(
              "text-xs tabular-nums",
              isOverLimit ? "text-red-500 font-medium" : "text-text-secondary"
            )}
          >
            {charCount}/{MAX_MESSAGE_LENGTH}
          </span>
        )}
      </div>

      {/* Disclaimer and crisis link */}
      <p className="mt-1 text-center text-[11px] leading-snug text-text-secondary">
        This chatbot provides support, not diagnosis. In crisis?{" "}
        <a
          href="tel:8009112000"
          className="underline underline-offset-2 hover:text-text-primary transition-colors"
        >
          Call 800-911-2000
        </a>
      </p>
      <p className="mt-0.5 text-center">
        <button
          type="button"
          onClick={showCrisisBanner}
          className="text-[11px] font-medium text-accent underline underline-offset-2 hover:text-accent/80 transition-colors"
        >
          Need help now?
        </button>
      </p>
    </div>
  );
}
