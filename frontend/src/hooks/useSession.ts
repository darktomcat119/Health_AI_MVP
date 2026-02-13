"use client";

import { useCallback } from "react";
import { useChatStore } from "@/stores/chatStore";
import { getHistory } from "@/services/api";
import type { Session, Message } from "@/types";

/** Return type of the useSession hook. */
interface UseSessionReturn {
  /** All available chat sessions. */
  sessions: Session[];
  /** The currently active session ID, or null if none. */
  activeSessionId: string | null;
  /**
   * Create a new chat session.
   * Resets the active session, clears messages, and prepares
   * the store for a fresh conversation.
   */
  createNewSession: () => void;
  /**
   * Switch to an existing session by ID.
   * Aborts any active stream, sets the session as active,
   * and loads its message history from the backend API.
   *
   * @param sessionId - The ID of the session to switch to.
   */
  switchSession: (sessionId: string) => Promise<void>;
  /**
   * Load the message history for a given session from the backend
   * and populate the store with the retrieved messages.
   *
   * @param sessionId - The ID of the session whose history to load.
   */
  loadSessionHistory: (sessionId: string) => Promise<void>;
}

/**
 * Session management hook for creating, switching, and loading
 * conversation sessions.
 *
 * Wraps the chat store's session actions and augments `switchSession`
 * with automatic history loading from the backend API.
 *
 * @returns An object with session state and management functions.
 *
 * @example
 * ```tsx
 * const { sessions, activeSessionId, createNewSession, switchSession } = useSession();
 *
 * return (
 *   <ul>
 *     {sessions.map((s) => (
 *       <li key={s.id} onClick={() => switchSession(s.id)}>
 *         {s.title}
 *       </li>
 *     ))}
 *     <button onClick={createNewSession}>New Chat</button>
 *   </ul>
 * );
 * ```
 */
export function useSession(): UseSessionReturn {
  const sessions = useChatStore((state) => state.sessions);
  const activeSessionId = useChatStore((state) => state.activeSessionId);

  const createNewSessionAction = useChatStore((state) => state.createNewSession);
  const switchSessionAction = useChatStore((state) => state.switchSession);
  const setMessages = useChatStore((state) => state.setMessages);
  const updateSessionRisk = useChatStore((state) => state.updateSessionRisk);

  /**
   * Load session history from the backend API and populate the store
   * with the converted message objects.
   */
  const loadSessionHistory = useCallback(
    async (sessionId: string): Promise<void> => {
      const historyResponse = await getHistory(sessionId);

      const messages: Message[] = historyResponse.history.map(
        (entry, index) => ({
          id: `${sessionId}_${index}_${entry.timestamp}`,
          role: entry.role as Message["role"],
          content: entry.content,
          timestamp: new Date(entry.timestamp),
          riskScore: entry.risk_score ?? undefined,
        })
      );

      setMessages(messages);

      if (historyResponse.cumulative_risk > 0) {
        /** Derive a risk level from the cumulative risk score. */
        const riskLevel =
          historyResponse.cumulative_risk >= 0.8
            ? "critical"
            : historyResponse.cumulative_risk >= 0.5
              ? "high"
              : historyResponse.cumulative_risk >= 0.3
                ? "medium"
                : "low";
        updateSessionRisk(sessionId, riskLevel);
      }
    },
    [setMessages, updateSessionRisk]
  );

  /**
   * Switch to an existing session and load its history from the backend.
   */
  const switchSession = useCallback(
    async (sessionId: string): Promise<void> => {
      switchSessionAction(sessionId);
      await loadSessionHistory(sessionId);
    },
    [switchSessionAction, loadSessionHistory]
  );

  return {
    sessions,
    activeSessionId,
    createNewSession: createNewSessionAction,
    switchSession,
    loadSessionHistory,
  };
}
