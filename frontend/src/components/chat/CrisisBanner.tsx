"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Phone, X } from "lucide-react";
import { useUIStore } from "@/stores/uiStore";
import { CRISIS_RESOURCES } from "@/utils/constants";
import { cn } from "@/utils/cn";

/**
 * Dismissible crisis-resource banner that slides down from the top.
 *
 * Renders Mexican crisis hotline numbers (Linea de la Vida, SAPTEL, 911)
 * as click-to-call links. The banner uses the crisis theme tokens
 * (warm amber/orange) and can be dismissed via the X button, which calls
 * `useUIStore.hideCrisisBanner()`.
 */
export function CrisisBanner() {
  const crisisBannerVisible = useUIStore((s) => s.crisisBannerVisible);
  const hideCrisisBanner = useUIStore((s) => s.hideCrisisBanner);

  return (
    <AnimatePresence>
      {crisisBannerVisible && (
        <motion.div
          initial={{ y: -100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -100, opacity: 0 }}
          transition={{ type: "spring", damping: 20, stiffness: 300 }}
          className={cn(
            "mx-4 mt-3 rounded-xl bg-crisis-bg p-4 shadow-md",
            "text-crisis-text sm:mx-6"
          )}
          role="alert"
        >
          <div className="flex items-start gap-3">
            {/* Content */}
            <div className="flex-1">
              <p className="mb-2 text-sm font-semibold">
                If you are in immediate danger, please reach out:
              </p>

              <ul className="space-y-1.5">
                {CRISIS_RESOURCES.map((resource) => (
                  <li key={resource.number} className="flex items-center gap-2">
                    <Phone className="h-3.5 w-3.5 shrink-0" />
                    <a
                      href={`tel:${resource.number.replace(/\s/g, "")}`}
                      className={cn(
                        "text-sm font-medium underline underline-offset-2",
                        "transition-opacity hover:opacity-80"
                      )}
                    >
                      {resource.name}: {resource.number}
                    </a>
                    <span className="text-xs opacity-70">
                      &mdash; {resource.description}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Dismiss button */}
            <button
              type="button"
              onClick={hideCrisisBanner}
              className={cn(
                "shrink-0 rounded-lg p-1.5",
                "transition-colors hover:bg-crisis-text/10"
              )}
              aria-label="Dismiss crisis resources banner"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
