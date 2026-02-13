import { create } from "zustand";

type Theme = "light" | "dark";

interface UIState {
  /** Whether the sidebar is open (relevant for mobile). */
  sidebarOpen: boolean;
  /** Current theme. */
  theme: Theme;
  /** Whether the crisis banner is visible. */
  crisisBannerVisible: boolean;
  /** Whether a professional handoff is active. */
  handoffActive: boolean;

  /** Toggle sidebar open/closed. */
  toggleSidebar: () => void;
  /** Set sidebar state explicitly. */
  setSidebarOpen: (open: boolean) => void;
  /** Set the theme. */
  setTheme: (theme: Theme) => void;
  /** Toggle between light and dark theme. */
  toggleTheme: () => void;
  /** Show the crisis banner. */
  showCrisisBanner: () => void;
  /** Hide the crisis banner. */
  hideCrisisBanner: () => void;
  /** Set handoff active state. */
  setHandoffActive: (active: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: false,
  theme: "light",
  crisisBannerVisible: false,
  handoffActive: false,

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),

  setTheme: (theme: Theme) => set({ theme }),

  toggleTheme: () =>
    set((state) => ({
      theme: state.theme === "light" ? "dark" : "light",
    })),

  showCrisisBanner: () => set({ crisisBannerVisible: true }),

  hideCrisisBanner: () => set({ crisisBannerVisible: false }),

  setHandoffActive: (active: boolean) => set({ handoffActive: active }),
}));
