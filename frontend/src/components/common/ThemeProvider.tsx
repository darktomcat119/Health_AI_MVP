"use client";

import { useEffect } from "react";
import { useUIStore } from "@/stores/uiStore";

interface ThemeProviderProps {
  children: React.ReactNode;
}

/**
 * Theme provider that applies dark/light mode class to the document.
 * Reads initial theme from localStorage or system preference.
 */
export function ThemeProvider({ children }: ThemeProviderProps) {
  const theme = useUIStore((state) => state.theme);
  const setTheme = useUIStore((state) => state.setTheme);

  useEffect(() => {
    const stored = localStorage.getItem("theme");
    if (stored === "dark" || stored === "light") {
      setTheme(stored);
    } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      setTheme("dark");
    }
  }, [setTheme]);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  return <>{children}</>;
}
