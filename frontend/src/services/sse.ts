import { API_BASE } from "@/utils/constants";
import type { CrisisResource, MessageMetadata } from "@/types";

/** Callbacks for handling SSE stream events. */
export interface SSECallbacks {
  onMetadata: (data: MessageMetadata) => void;
  onToken: (token: string) => void;
  onCrisis: (resources: CrisisResource[]) => void;
  onDone: (data: { session_message_count: number }) => void;
  onError: (error: Error) => void;
}

/**
 * Stream a chat response via Server-Sent Events.
 *
 * Connects to the SSE endpoint, reads the response body as a stream,
 * and routes parsed events to the appropriate callbacks.
 *
 * @returns AbortController for cancelling the stream.
 */
export function streamChat(
  sessionId: string | null,
  message: string,
  callbacks: SSECallbacks
): AbortController {
  const controller = new AbortController();

  processStream(sessionId, message, callbacks, controller.signal).catch(
    (error) => {
      if (error instanceof Error && error.name === "AbortError") {
        return;
      }
      callbacks.onError(
        error instanceof Error ? error : new Error("Stream failed")
      );
    }
  );

  return controller;
}

/**
 * Internal async function that handles the SSE stream processing.
 */
async function processStream(
  sessionId: string | null,
  message: string,
  callbacks: SSECallbacks,
  signal: AbortSignal
): Promise<void> {
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_message: message,
      session_id: sessionId,
    }),
    signal,
  });

  if (!response.ok) {
    throw new Error(`Stream request failed with status ${response.status}`);
  }

  if (!response.body) {
    throw new Error("Response body is null");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");

      // Keep the last potentially incomplete line in the buffer
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith("data: ")) continue;

        const jsonStr = trimmed.slice(6);
        try {
          const data = JSON.parse(jsonStr);
          routeEvent(data, callbacks);
        } catch {
          // Skip malformed JSON lines
        }
      }
    }

    // Process any remaining buffer
    if (buffer.trim().startsWith("data: ")) {
      const jsonStr = buffer.trim().slice(6);
      try {
        const data = JSON.parse(jsonStr);
        routeEvent(data, callbacks);
      } catch {
        // Skip malformed final line
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Route a parsed SSE event to the appropriate callback.
 */
function routeEvent(
  data: Record<string, unknown>,
  callbacks: SSECallbacks
): void {
  switch (data.type) {
    case "metadata":
      callbacks.onMetadata(data as unknown as MessageMetadata);
      break;
    case "token":
      callbacks.onToken(data.content as string);
      break;
    case "crisis":
      callbacks.onCrisis(data.resources as CrisisResource[]);
      break;
    case "done":
      callbacks.onDone(data as unknown as { session_message_count: number });
      break;
  }
}
