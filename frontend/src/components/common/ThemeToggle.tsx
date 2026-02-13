"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/hooks/useTheme";
import { cn } from "@/utils/cn";

interface ThemeToggleProps {
  /** Additional CSS classes. */
  className?: string;
}

/**
 * Dark/light mode toggle button.
 * Switches between sun and moon icons based on current theme.
 */
export function ThemeToggle({ className }: ThemeToggleProps) {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={cn(
        "p-2 rounded-lg transition-colors",
        "hover:bg-bg-chat text-text-secondary hover:text-text-primary",
        className
      )}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      type="button"
    >
      {isDark ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
}
