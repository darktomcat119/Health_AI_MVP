"use client";

import { useCallback } from "react";
import { useChatStore } from "@/stores/chatStore";
import { useUIStore } from "@/stores/uiStore";
import { streamChat } from "@/services/sse";
import type { Message, MessageMetadata, CrisisResource } from "@/types";

/** Return type of the useChat hook. */
interface UseChatReturn {
  /** Messages in the current active session. */
  messages: Message[];
  /** Whether a bot response is currently being streamed. */
  isStreaming: boolean;
  /**
   * Send a user message and begin streaming the assistant response.
   * Orchestrates the full lifecycle: adds the user message to the store,
   * initiates the SSE stream, and routes all stream events to the
   * appropriate store actions and UI updates.
   *
   * @param content - The text content of the user message.
   */
  sendMessage: (content: string) => void;
  /**
   * Stop the currently active stream, aborting the SSE connection
   * and cleaning up streaming state in the store.
   */
  stopStreaming: () => void;
}

/**
 * Core chat hook that provides message sending with SSE streaming,
 * message history, and streaming state management.
 *
 * Integrates the chat store (state management), SSE service (streaming),
 * and UI store (crisis banner) into a single cohesive interface.
 *
 * @returns An object containing messages, streaming state, and action functions.
 *
 * @example
 * ```tsx
 * const { messages, isStreaming, sendMessage, stopStreaming } = useChat();
 *
 * const handleSubmit = (text: string) => {
 *   sendMessage(text);
 * };
 * ```
 */
export function useChat(): UseChatReturn {
  const messages = useChatStore((state) => state.messages);
  const isStreaming = useChatStore((state) => state.isStreaming);
  const activeSessionId = useChatStore((state) => state.activeSessionId);

  const addUserMessage = useChatStore((state) => state.addUserMessage);
  const startStreaming = useChatStore((state) => state.startStreaming);
  const appendStreamToken = useChatStore((state) => state.appendStreamToken);
  const replaceStreamContent = useChatStore((state) => state.replaceStreamContent);
  const finalizeStream = useChatStore((state) => state.finalizeStream);
  const stopStreamingAction = useChatStore((state) => state.stopStreaming);
  const setActiveSession = useChatStore((state) => state.setActiveSession);
  const updateSessionRisk = useChatStore((state) => state.updateSessionRisk);

  const showCrisisBanner = useUIStore((state) => state.showCrisisBanner);

  /** Accumulated metadata from the stream, used at finalization. */
  const sendMessage = useCallback(
    (content: string) => {
      if (!content.trim()) {
        return;
      }

      addUserMessage(content);

      /** Tracks the latest metadata received from the stream. */
      let latestMetadata: MessageMetadata | null = null;
      /** Tracks the session message count from the done event. */
      let sessionMessageCount: number | undefined;

      const controller = streamChat(activeSessionId, content, {
        onMetadata: (data: MessageMetadata) => {
          latestMetadata = data;
          setActiveSession(data.session_id, content.slice(0, 40));
          updateSessionRisk(data.session_id, data.risk_level);
        },

        onToken: (token: string) => {
          appendStreamToken(token);
        },

        onCrisis: (_resources: CrisisResource[]) => {
          showCrisisBanner();
        },

        onReplace: (content: string) => {
          replaceStreamContent(content);
        },

        onDone: (data: { session_message_count: number }) => {
          sessionMessageCount = data.session_message_count;
          finalizeStream({
            riskScore: latestMetadata?.risk_score,
            riskLevel: latestMetadata?.risk_level,
            triageActivated: latestMetadata?.triage_activated,
            humanHandoff: latestMetadata?.human_handoff,
            messageCount: sessionMessageCount,
          });
        },

        onError: (_error: Error) => {
          stopStreamingAction();
        },
      });

      startStreaming(controller);
    },
    [
      activeSessionId,
      addUserMessage,
      startStreaming,
      appendStreamToken,
      replaceStreamContent,
      finalizeStream,
      stopStreamingAction,
      setActiveSession,
      updateSessionRisk,
      showCrisisBanner,
    ]
  );

  return {
    messages,
    isStreaming,
    sendMessage,
    stopStreaming: stopStreamingAction,
  };
}
