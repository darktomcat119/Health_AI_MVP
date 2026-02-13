import { create } from "zustand";
import type { Message, Session, RiskLevel, CrisisResource } from "@/types";

interface ChatState {
  /** All sessions the user has participated in. */
  sessions: Session[];
  /** Currently active session ID. */
  activeSessionId: string | null;
  /** Messages for the active session. */
  messages: Message[];
  /** Whether a response is currently being streamed. */
  isStreaming: boolean;
  /** Accumulated streaming content for the current bot message. */
  streamingContent: string;
  /** AbortController for cancelling the current stream. */
  abortController: AbortController | null;

  /** Create a new chat session. */
  createNewSession: () => void;
  /** Switch to a different session. */
  switchSession: (sessionId: string) => void;
  /** Set the active session ID and update session list. */
  setActiveSession: (sessionId: string, title: string) => void;
  /** Add a user message to the current conversation. */
  addUserMessage: (content: string) => void;
  /** Start streaming a bot response. */
  startStreaming: (abortController: AbortController) => void;
  /** Append a token to the streaming message. */
  appendStreamToken: (token: string) => void;
  /** Finalize the stream and convert to a regular message. */
  finalizeStream: (metadata: {
    riskScore?: number;
    riskLevel?: RiskLevel;
    triageActivated?: boolean;
    humanHandoff?: boolean;
    messageCount?: number;
  }) => void;
  /** Stop the current stream. */
  stopStreaming: () => void;
  /** Update session risk level. */
  updateSessionRisk: (sessionId: string, riskLevel: RiskLevel) => void;
  /** Set messages for a session (e.g., from history load). */
  setMessages: (messages: Message[]) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  messages: [],
  isStreaming: false,
  streamingContent: "",
  abortController: null,

  createNewSession: () => {
    set({
      activeSessionId: null,
      messages: [],
      isStreaming: false,
      streamingContent: "",
    });
  },

  switchSession: (sessionId: string) => {
    const { isStreaming, abortController } = get();
    if (isStreaming && abortController) {
      abortController.abort();
    }
    set({
      activeSessionId: sessionId,
      messages: [],
      isStreaming: false,
      streamingContent: "",
      abortController: null,
    });
  },

  setActiveSession: (sessionId: string, title: string) => {
    const { sessions } = get();
    const exists = sessions.find((s) => s.id === sessionId);
    if (!exists) {
      const newSession: Session = {
        id: sessionId,
        title: title.slice(0, 40),
        messageCount: 0,
        riskLevel: "low",
        createdAt: new Date(),
        lastActivity: new Date(),
      };
      set({ sessions: [newSession, ...sessions], activeSessionId: sessionId });
    } else {
      set({ activeSessionId: sessionId });
    }
  },

  addUserMessage: (content: string) => {
    const message: Message = {
      id: `msg_${Date.now()}_user`,
      role: "user",
      content,
      timestamp: new Date(),
    };
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  startStreaming: (abortController: AbortController) => {
    const streamingMessage: Message = {
      id: `msg_${Date.now()}_bot`,
      role: "assistant",
      content: "",
      timestamp: new Date(),
      isStreaming: true,
    };
    set((state) => ({
      isStreaming: true,
      streamingContent: "",
      abortController,
      messages: [...state.messages, streamingMessage],
    }));
  },

  appendStreamToken: (token: string) => {
    set((state) => {
      const newContent = state.streamingContent + token;
      const updatedMessages = state.messages.map((msg) =>
        msg.isStreaming ? { ...msg, content: newContent } : msg
      );
      return {
        streamingContent: newContent,
        messages: updatedMessages,
      };
    });
  },

  finalizeStream: (metadata) => {
    set((state) => {
      const updatedMessages = state.messages.map((msg) =>
        msg.isStreaming
          ? {
              ...msg,
              isStreaming: false,
              riskScore: metadata.riskScore,
              riskLevel: metadata.riskLevel,
              triageActivated: metadata.triageActivated,
              humanHandoff: metadata.humanHandoff,
            }
          : msg
      );

      const updatedSessions = state.sessions.map((s) =>
        s.id === state.activeSessionId
          ? {
              ...s,
              messageCount: metadata.messageCount ?? s.messageCount,
              lastActivity: new Date(),
            }
          : s
      );

      return {
        messages: updatedMessages,
        isStreaming: false,
        streamingContent: "",
        abortController: null,
        sessions: updatedSessions,
      };
    });
  },

  stopStreaming: () => {
    const { abortController } = get();
    if (abortController) {
      abortController.abort();
    }
    set((state) => {
      const updatedMessages = state.messages.map((msg) =>
        msg.isStreaming ? { ...msg, isStreaming: false } : msg
      );
      return {
        messages: updatedMessages,
        isStreaming: false,
        streamingContent: "",
        abortController: null,
      };
    });
  },

  updateSessionRisk: (sessionId: string, riskLevel: RiskLevel) => {
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.id === sessionId ? { ...s, riskLevel } : s
      ),
    }));
  },

  setMessages: (messages: Message[]) => {
    set({ messages });
  },
}));
