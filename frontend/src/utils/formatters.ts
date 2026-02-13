import { format, formatDistanceToNow, isToday, isYesterday } from "date-fns";

/**
 * Format a timestamp for display in message bubbles.
 * Shows "2:34 PM" format.
 */
export function formatMessageTime(date: Date): string {
  return format(date, "h:mm a");
}

/**
 * Format a date for session list display.
 * Shows "Today", "Yesterday", or the date.
 */
export function formatSessionDate(date: Date): string {
  if (isToday(date)) {
    return "Today";
  }
  if (isYesterday(date)) {
    return "Yesterday";
  }
  return format(date, "MMM d");
}

/**
 * Format a relative time string like "5 minutes ago".
 */
export function formatRelativeTime(date: Date): string {
  return formatDistanceToNow(date, { addSuffix: true });
}

/**
 * Truncate text to a maximum length with ellipsis.
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength).trimEnd()}...`;
}
