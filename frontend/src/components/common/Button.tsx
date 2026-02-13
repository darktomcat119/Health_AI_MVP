"use client";

import { forwardRef } from "react";
import { cn } from "@/utils/cn";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style variant. */
  variant?: ButtonVariant;
  /** Size variant. */
  size?: ButtonSize;
  /** Full width button. */
  fullWidth?: boolean;
}

const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  primary: "bg-accent text-white hover:bg-accent/90",
  secondary: "bg-bg-secondary text-text-primary border border-border hover:bg-bg-chat",
  ghost: "text-text-secondary hover:text-text-primary hover:bg-bg-chat",
  danger: "bg-red-600 text-white hover:bg-red-700",
};

const SIZE_CLASSES: Record<ButtonSize, string> = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2 text-sm",
  lg: "px-6 py-3 text-base",
};

/**
 * Reusable button component with variants and sizes.
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(
    { variant = "primary", size = "md", fullWidth = false, className, children, ...props },
    ref
  ) {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-lg font-medium transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50",
          "disabled:opacity-50 disabled:pointer-events-none",
          VARIANT_CLASSES[variant],
          SIZE_CLASSES[size],
          fullWidth && "w-full",
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);
