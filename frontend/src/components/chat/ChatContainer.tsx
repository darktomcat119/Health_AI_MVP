"use client";

import { useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, AlertTriangle, PhoneCall, X } from "lucide-react";
import { useChat } from "@/hooks/useChat";
import { useAutoScroll } from "@/hooks/useAutoScroll";
import { useUIStore } from "@/stores/uiStore";
import { cn } from "@/utils/cn";
import { CRISIS_RESOURCES } from "@/utils/constants";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { StreamingMessage } from "@/components/chat/StreamingMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import type { Message } from "@/types";

/**
 * Determine whether to show the typing indicator.
 * True when the last message is from the user and we are streaming
 * but no tokens have arrived yet (i.e. no streaming message exists yet,
 * or the streaming message content is still empty).
 */
function shouldShowTypingIndicator(
  messages: Message[],
  isStreaming: boolean
): boolean {
  if (!isStreaming || messages.length === 0) {
    return false;
  }
  const last = messages[messages.length - 1];
  if (last.role === "user") {
    return true;
  }
  if (last.role === "assistant" && last.isStreaming && last.content === "") {
    return true;
  }
  return false;
}

/** Animated typing dots shown while waiting for the first streamed token. */
function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 px-4 sm:px-6">
      <div
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent"
        aria-hidden="true"
      >
        <span className="text-sm font-semibold">AI</span>
      </div>
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-md bg-bg-bot-bubble px-4 py-3">
        <span
          className="h-2 w-2 rounded-full bg-text-secondary animate-bounce-dots"
          style={{ animationDelay: "0ms" }}
        />
        <span
          className="h-2 w-2 rounded-full bg-text-secondary animate-bounce-dots"
          style={{ animationDelay: "160ms" }}
        />
        <span
          className="h-2 w-2 rounded-full bg-text-secondary animate-bounce-dots"
          style={{ animationDelay: "320ms" }}
        />
        <span className="sr-only">Assistant is typing</span>
      </div>
    </div>
  );
}

/** Welcome screen shown when the conversation has no messages yet. */
function WelcomeScreen() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 text-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="max-w-md"
      >
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-accent/10">
          <span className="text-2xl font-bold text-accent">AI</span>
        </div>
        <h2 className="mb-3 text-xl font-semibold text-text-primary">
          Welcome to your safe space
        </h2>
        <p className="mb-6 text-sm leading-relaxed text-text-secondary">
          I&apos;m here to listen and support you. Everything you share is
          confidential. You can talk about anything that&apos;s on your mind.
        </p>
        <p className="text-xs text-text-secondary">
          Type a message below to get started.
        </p>
      </motion.div>
    </div>
  );
}

/** Crisis resource banner displayed when a crisis event is detected. */
function CrisisBanner() {
  const crisisBannerVisible = useUIStore((s) => s.crisisBannerVisible);
  const hideCrisisBanner = useUIStore((s) => s.hideCrisisBanner);

  return (
    <AnimatePresence>
      {crisisBannerVisible && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="overflow-hidden"
        >
          <div className="flex items-start gap-3 bg-crisis-bg px-4 py-3 text-crisis-text sm:px-6">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-semibold">
                If you are in immediate danger, please reach out:
              </p>
              <ul className="mt-1 space-y-0.5">
                {CRISIS_RESOURCES.map((resource) => (
                  <li key={resource.number} className="text-xs">
                    <a
                      href={`tel:${resource.number.replace(/\s/g, "")}`}
                      className="font-medium underline underline-offset-2"
                    >
                      {resource.name}: {resource.number}
                    </a>
                    <span className="ml-1 opacity-80">
                      &mdash; {resource.description}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
            <button
              type="button"
              onClick={hideCrisisBanner}
              className="shrink-0 rounded p-1 hover:bg-crisis-text/10 transition-colors"
              aria-label="Dismiss crisis resources banner"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/** Notice shown when a professional handoff has been triggered. */
function HandoffNotice() {
  const handoffActive = useUIStore((s) => s.handoffActive);

  return (
    <AnimatePresence>
      {handoffActive && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="overflow-hidden"
        >
          <div className="flex items-center gap-3 bg-accent/10 px-4 py-3 text-accent sm:px-6">
            <PhoneCall className="h-5 w-5 shrink-0" />
            <p className="text-sm font-medium">
              A professional has been notified and will follow up with you.
              Continue chatting in the meantime.
            </p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * Main chat container that orchestrates the message list, streaming,
 * auto-scroll behavior, and the input area.
 */
export function ChatContainer() {
  const { messages, isStreaming, sendMessage, stopStreaming } = useChat();
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const { scrollToBottom, showScrollButton } = useAutoScroll(
    scrollContainerRef,
    [messages.length, messages[messages.length - 1]?.content]
  );

  const hasMessages = messages.length > 0;
  const showTyping = shouldShowTypingIndicator(messages, isStreaming);

  /**
   * Find the currently streaming message (if any) so we can render it
   * with the StreamingMessage component instead of a regular bubble.
   */
  const streamingMessage = messages.find(
    (m) => m.isStreaming && m.role === "assistant"
  );

  return (
    <div className="flex h-full flex-col bg-bg-chat">
      {/* Crisis banner and handoff notice pinned above messages */}
      <CrisisBanner />
      <HandoffNotice />

      {/* Scrollable messages area */}
      <div
        ref={scrollContainerRef}
        className="relative flex flex-1 flex-col overflow-y-auto"
      >
        {!hasMessages ? (
          <WelcomeScreen />
        ) : (
          <div className="flex flex-col gap-4 py-4">
            <AnimatePresence initial={false}>
              {messages.map((message) => {
                if (
                  message.isStreaming &&
                  message.role === "assistant" &&
                  streamingMessage
                ) {
                  return (
                    <StreamingMessage
                      key={message.id}
                      content={message.content}
                      isStreaming={true}
                    />
                  );
                }
                return <MessageBubble key={message.id} message={message} />;
              })}
            </AnimatePresence>

            {showTyping && <TypingIndicator />}
          </div>
        )}

        {/* Floating scroll-to-bottom button */}
        <AnimatePresence>
          {showScrollButton && (
            <motion.button
              type="button"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.2 }}
              onClick={scrollToBottom}
              className={cn(
                "absolute bottom-4 left-1/2 -translate-x-1/2",
                "flex h-9 w-9 items-center justify-center",
                "rounded-full bg-bg-secondary text-text-secondary",
                "shadow-md border border-border",
                "hover:bg-bg-primary hover:text-text-primary",
                "transition-colors"
              )}
              aria-label="Scroll to bottom"
            >
              <ChevronDown className="h-5 w-5" />
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Fixed input area at the bottom */}
      <div className="shrink-0 shadow-[0_-1px_3px_rgba(0,0,0,0.05)]">
        <ChatInput
          onSend={sendMessage}
          isStreaming={isStreaming}
          onStop={stopStreaming}
        />
      </div>
    </div>
  );
}
