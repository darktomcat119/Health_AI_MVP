/** Risk level classification from the backend. */
export type RiskLevel = "low" | "medium" | "high" | "critical";

/** A single message in a conversation. */
export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  riskScore?: number;
  riskLevel?: RiskLevel;
  triageActivated?: boolean;
  humanHandoff?: boolean;
  isStreaming?: boolean;
}

/** A conversation session. */
export interface Session {
  id: string;
  title: string;
  messageCount: number;
  riskLevel: RiskLevel;
  createdAt: Date;
  lastActivity: Date;
}

/** Metadata received from SSE stream. */
export interface MessageMetadata {
  session_id: string;
  risk_score: number;
  risk_level: RiskLevel;
  triage_activated: boolean;
  human_handoff: boolean;
}

/** Crisis resource from the backend. */
export interface CrisisResource {
  name: string;
  number: string;
  hours: string;
  type: string;
  description: string;
}

/** Chat API response. */
export interface ChatResponse {
  session_id: string;
  bot_response: string;
  risk_score: number;
  risk_level: RiskLevel;
  triage_activated: boolean;
  human_handoff: boolean;
  crisis_resources: CrisisResource[] | null;
  session_message_count: number;
  timestamp: string;
}

/** Session history response from the API. */
export interface SessionHistoryResponse {
  session_id: string;
  history: MessageEntry[];
  message_count: number;
  cumulative_risk: number;
  triage_activated: boolean;
  created_at: string;
}

/** Single message entry from history API. */
export interface MessageEntry {
  role: string;
  content: string;
  risk_score: number | null;
  timestamp: string;
}

/** Handoff response from the API. */
export interface HandoffResponse {
  session_id: string;
  handoff_status: string;
  professional_context: Record<string, unknown>;
}

/** Health check response. */
export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  active_sessions: number;
}

/** SSE stream event types. */
export type SSEEventType = "metadata" | "token" | "crisis" | "done";

/** Parsed SSE event data. */
export interface SSEEvent {
  type: SSEEventType;
  [key: string]: unknown;
}
