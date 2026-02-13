"use client";

import { useUIStore } from "@/stores/uiStore";

/** Return type of the useTheme hook. */
interface UseThemeReturn {
  /** The current theme value: "light" or "dark". */
  theme: "light" | "dark";
  /**
   * Toggle between light and dark themes.
   * Delegates to the UI store's `toggleTheme` action.
   */
  toggleTheme: () => void;
  /** Whether the current theme is dark mode. */
  isDark: boolean;
}

/**
 * Simple theme hook that wraps the UI store's theme state.
 *
 * Provides the current theme, a toggle function, and a convenient
 * `isDark` boolean for conditional rendering and styling.
 *
 * @returns An object with theme state and the toggle function.
 *
 * @example
 * ```tsx
 * const { theme, toggleTheme, isDark } = useTheme();
 *
 * return (
 *   <button onClick={toggleTheme}>
 *     {isDark ? "Switch to Light" : "Switch to Dark"}
 *   </button>
 * );
 * ```
 */
export function useTheme(): UseThemeReturn {
  const theme = useUIStore((state) => state.theme);
  const toggleTheme = useUIStore((state) => state.toggleTheme);

  return {
    theme,
    toggleTheme,
    isDark: theme === "dark",
  };
}
