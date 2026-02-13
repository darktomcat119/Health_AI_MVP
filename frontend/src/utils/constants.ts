/** Base URL for the API, configured via environment variable. */
export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/** Risk level to color class mapping for indicators. */
export const RISK_COLOR_MAP: Record<string, string> = {
  low: "bg-green-500",
  medium: "bg-yellow-500",
  high: "bg-orange-500",
  critical: "bg-red-500",
} as const;

/** Risk level to pulse animation mapping. */
export const RISK_ANIMATION_MAP: Record<string, string> = {
  low: "",
  medium: "animate-pulse",
  high: "animate-pulse",
  critical: "animate-pulse-ring",
} as const;

/** Maximum character count for user messages. */
export const MAX_MESSAGE_LENGTH = 2000;

/** Character count at which to show the counter. */
export const SHOW_COUNTER_THRESHOLD = 1500;

/** Maximum lines the textarea can grow to. */
export const MAX_TEXTAREA_LINES = 4;

/** Sidebar width in pixels. */
export const SIDEBAR_WIDTH = 280;

/** Maximum title length for session display. */
export const MAX_SESSION_TITLE_LENGTH = 40;

/** Crisis hotline numbers for Mexico. */
export const CRISIS_RESOURCES = [
  {
    name: "Linea de la Vida",
    number: "800-911-2000",
    description: "Free, national, 24/7",
  },
  {
    name: "SAPTEL",
    number: "55 5259-8121",
    description: "24/7",
  },
  {
    name: "Emergency",
    number: "911",
    description: "Immediate emergency",
  },
] as const;
