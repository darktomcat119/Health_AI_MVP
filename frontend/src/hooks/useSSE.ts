"use client";

import { useCallback, useRef, useState } from "react";
import { streamChat, type SSECallbacks } from "@/services/sse";

/** Return type of the useSSE hook. */
interface UseSSEReturn {
  /** Whether an SSE connection is currently active. */
  isConnected: boolean;
  /**
   * Open a new SSE connection to the streaming chat endpoint.
   *
   * If a connection is already active, it will be disconnected first
   * before establishing the new one.
   *
   * @param sessionId - The session ID to stream for, or null for a new session.
   * @param message - The user message to send.
   * @param callbacks - Event callbacks for handling stream events.
   */
  connectStream: (
    sessionId: string | null,
    message: string,
    callbacks: SSECallbacks
  ) => void;
  /**
   * Disconnect the current SSE stream by aborting the underlying
   * AbortController. Safe to call when no connection is active.
   */
  disconnect: () => void;
}

/**
 * Low-level SSE hook that wraps the `streamChat` service with
 * connection state tracking and lifecycle management.
 *
 * Provides a reactive `isConnected` state, a `connectStream` function
 * to initiate streams with automatic cleanup of prior connections,
 * and a `disconnect` function for manual teardown.
 *
 * This hook is intended for advanced use cases where direct SSE control
 * is needed. For typical chat interactions, prefer `useChat` instead.
 *
 * @returns An object with connection state and control functions.
 *
 * @example
 * ```tsx
 * const { isConnected, connectStream, disconnect } = useSSE();
 *
 * connectStream(sessionId, "Hello", {
 *   onMetadata: (meta) => { ... },
 *   onToken: (token) => { ... },
 *   onCrisis: (resources) => { ... },
 *   onDone: (data) => { ... },
 *   onError: (err) => { ... },
 * });
 * ```
 */
export function useSSE(): UseSSEReturn {
  const [isConnected, setIsConnected] = useState(false);
  const controllerRef = useRef<AbortController | null>(null);

  const disconnect = useCallback(() => {
    if (controllerRef.current) {
      controllerRef.current.abort();
      controllerRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const connectStream = useCallback(
    (
      sessionId: string | null,
      message: string,
      callbacks: SSECallbacks
    ) => {
      // Disconnect any existing stream before starting a new one
      if (controllerRef.current) {
        controllerRef.current.abort();
        controllerRef.current = null;
      }

      setIsConnected(true);

      /** Wraps the original callbacks to track connection lifecycle. */
      const wrappedCallbacks: SSECallbacks = {
        onMetadata: (data) => {
          callbacks.onMetadata(data);
        },
        onToken: (token) => {
          callbacks.onToken(token);
        },
        onCrisis: (resources) => {
          callbacks.onCrisis(resources);
        },
        onDone: (data) => {
          setIsConnected(false);
          controllerRef.current = null;
          callbacks.onDone(data);
        },
        onError: (error) => {
          setIsConnected(false);
          controllerRef.current = null;
          callbacks.onError(error);
        },
      };

      const controller = streamChat(sessionId, message, wrappedCallbacks);
      controllerRef.current = controller;
    },
    []
  );

  return {
    isConnected,
    connectStream,
    disconnect,
  };
}
