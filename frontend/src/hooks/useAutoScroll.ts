"use client";

import { useCallback, useEffect, useRef, useState, type RefObject } from "react";

/** Pixel threshold from the bottom to consider the user "at the bottom". */
const SCROLL_THRESHOLD_PX = 100;

/** Return type of the useAutoScroll hook. */
interface UseAutoScrollReturn {
  /**
   * Programmatically scroll to the bottom of the container.
   * Uses smooth scrolling behavior for a polished UX.
   */
  scrollToBottom: () => void;
  /**
   * Whether to show a "scroll to bottom" button.
   * True when the user has manually scrolled up away from the bottom.
   */
  showScrollButton: boolean;
}

/**
 * Smart auto-scroll hook for chat-style scroll containers.
 *
 * Monitors a scroll container element and automatically scrolls to the
 * bottom when new content arrives, unless the user has manually scrolled
 * up to review previous messages. When the user scrolls away from the
 * bottom, a `showScrollButton` flag is set to true so the UI can render
 * a "scroll to bottom" indicator.
 *
 * Uses scroll position detection to determine whether the user is
 * near the bottom of the container.
 *
 * @param containerRef - A React ref pointing to the scrollable container element.
 * @param dependencies - An array of values that, when changed, trigger an auto-scroll
 *                       attempt (e.g., messages array length, streaming content).
 * @returns An object with `scrollToBottom` and `showScrollButton`.
 *
 * @example
 * ```tsx
 * const containerRef = useRef<HTMLDivElement>(null);
 * const { scrollToBottom, showScrollButton } = useAutoScroll(containerRef, [messages.length]);
 *
 * return (
 *   <div ref={containerRef} style={{ overflowY: "auto" }}>
 *     {messages.map(renderMessage)}
 *     {showScrollButton && (
 *       <button onClick={scrollToBottom}>Scroll to bottom</button>
 *     )}
 *   </div>
 * );
 * ```
 */
export function useAutoScroll(
  containerRef: RefObject<HTMLElement | null>,
  dependencies: ReadonlyArray<unknown>
): UseAutoScrollReturn {
  const [showScrollButton, setShowScrollButton] = useState(false);

  /**
   * Tracks whether the user is near the bottom of the scroll container.
   * Updated on every scroll event. Used to decide whether to auto-scroll.
   */
  const isNearBottomRef = useRef(true);

  /**
   * Check if the scroll position is within the threshold of the bottom.
   */
  const checkIfNearBottom = useCallback((element: HTMLElement): boolean => {
    const { scrollTop, scrollHeight, clientHeight } = element;
    return scrollHeight - scrollTop - clientHeight <= SCROLL_THRESHOLD_PX;
  }, []);

  /**
   * Scroll the container to the absolute bottom.
   */
  const scrollToBottom = useCallback(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });

    isNearBottomRef.current = true;
    setShowScrollButton(false);
  }, [containerRef]);

  /**
   * Listen for scroll events on the container to detect manual scrolling.
   */
  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }

    const handleScroll = (): void => {
      const nearBottom = checkIfNearBottom(container);
      isNearBottomRef.current = nearBottom;
      setShowScrollButton(!nearBottom);
    };

    container.addEventListener("scroll", handleScroll, { passive: true });

    return () => {
      container.removeEventListener("scroll", handleScroll);
    };
  }, [containerRef, checkIfNearBottom]);

  /**
   * Auto-scroll when dependencies change, but only if the user
   * hasn't manually scrolled up.
   */
  useEffect(() => {
    if (!isNearBottomRef.current) {
      return;
    }

    const container = containerRef.current;
    if (!container) {
      return;
    }

    /**
     * Use requestAnimationFrame to ensure the DOM has updated
     * with new content before scrolling.
     */
    const frameId = requestAnimationFrame(() => {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: "smooth",
      });
    });

    return () => {
      cancelAnimationFrame(frameId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- dependencies is the caller's trigger array
  }, dependencies);

  return {
    scrollToBottom,
    showScrollButton,
  };
}
