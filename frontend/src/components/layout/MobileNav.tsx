"use client";

import { MessageCircle, Phone, Settings } from "lucide-react";
import { useUIStore } from "@/stores/uiStore";
import { cn } from "@/utils/cn";

/**
 * Mobile bottom navigation bar.
 * Provides quick access to chat, crisis resources, and settings.
 */
export function MobileNav() {
  const showCrisisBanner = useUIStore((state) => state.showCrisisBanner);
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);

  return (
    <nav
      className="flex items-center justify-around py-2 px-4 border-t border-border bg-bg-secondary"
      role="navigation"
      aria-label="Mobile navigation"
    >
      <NavButton
        icon={<MessageCircle size={20} />}
        label="Chat"
        onClick={toggleSidebar}
      />
      <NavButton
        icon={<Phone size={20} />}
        label="Help Now"
        onClick={showCrisisBanner}
        highlight
      />
      <NavButton
        icon={<Settings size={20} />}
        label="Settings"
        onClick={toggleSidebar}
      />
    </nav>
  );
}

interface NavButtonProps {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  highlight?: boolean;
}

function NavButton({ icon, label, onClick, highlight = false }: NavButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex flex-col items-center gap-0.5 p-2 rounded-lg transition-colors min-w-[60px]",
        highlight
          ? "text-crisis-text"
          : "text-text-secondary hover:text-text-primary"
      )}
      type="button"
      aria-label={label}
    >
      {icon}
      <span className="text-[10px] font-medium">{label}</span>
    </button>
  );
}
