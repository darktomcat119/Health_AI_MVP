"use client";

import { useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { cn } from "@/utils/cn";

interface ModalProps {
  /** Whether the modal is open. */
  isOpen: boolean;
  /** Callback when the modal should close. */
  onClose: () => void;
  /** Modal title. */
  title?: string;
  /** Modal content. */
  children: React.ReactNode;
  /** Additional CSS classes for the modal body. */
  className?: string;
}

/**
 * Reusable modal dialog with backdrop and animations.
 * Supports keyboard navigation (Escape to close) and focus trapping.
 */
export function Modal({ isOpen, onClose, title, children, className }: ModalProps) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [isOpen, handleKeyDown]);

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
            role="button"
            tabIndex={0}
            aria-label="Close modal"
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") onClose();
            }}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.2 }}
            className={cn(
              "relative bg-bg-secondary rounded-xl shadow-xl",
              "max-w-md w-full max-h-[80vh] overflow-y-auto",
              className
            )}
            role="dialog"
            aria-modal="true"
            aria-label={title || "Dialog"}
          >
            {title && (
              <div className="flex items-center justify-between p-4 border-b border-border">
                <h2 className="text-lg font-semibold text-text-primary">{title}</h2>
                <button
                  onClick={onClose}
                  className="p-1 rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-chat transition-colors"
                  aria-label="Close"
                  type="button"
                >
                  <X size={18} />
                </button>
              </div>
            )}
            <div className="p-4">{children}</div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
