import { API_BASE } from "@/utils/constants";
import type {
  ChatResponse,
  HealthResponse,
  SessionHistoryResponse,
  HandoffResponse,
} from "@/types";

/** Default request timeout in milliseconds. */
const REQUEST_TIMEOUT_MS = 30_000;

/** API error with typed status code. */
class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Execute a fetch request with timeout and error handling.
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs: number = REQUEST_TIMEOUT_MS
): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new ApiError(
        body.detail || `Request failed with status ${response.status}`,
        response.status
      );
    }

    return response;
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * Send a chat message and receive the full response.
 */
export async function sendMessage(
  userMessage: string,
  sessionId: string | null = null
): Promise<ChatResponse> {
  const response = await fetchWithTimeout(`${API_BASE}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_message: userMessage,
      session_id: sessionId,
    }),
  });

  return response.json();
}

/**
 * Get full conversation history for a session.
 */
export async function getHistory(
  sessionId: string
): Promise<SessionHistoryResponse> {
  const response = await fetchWithTimeout(`${API_BASE}/chat/${sessionId}/history`);
  return response.json();
}

/**
 * Trigger a manual professional handoff for a session.
 */
export async function triggerHandoff(
  sessionId: string
): Promise<HandoffResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE}/chat/${sessionId}/handoff`,
    { method: "POST" }
  );
  return response.json();
}

/**
 * Check the backend health status.
 */
export async function healthCheck(): Promise<HealthResponse> {
  const response = await fetchWithTimeout(`${API_BASE}/health`);
  return response.json();
}
