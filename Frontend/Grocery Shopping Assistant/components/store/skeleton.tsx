"use client"

import { memo } from "react"

export const Skeleton = memo(function Skeleton({
  className = "",
  variant = "default",
  count = 1,
  children,
}: {
  className?: string
  variant?: "default" | "text" | "circular" | "rectangular"
  count?: number
  children?: React.ReactNode
}) {
  const baseClasses = "skeleton"
  const variantClasses = {
    default: "rounded-xl",
    text: "h-4 w-full rounded",
                                                                                                                                                                                                                                                                                                                                                                                                              er                     ON                st   /loadi     inner.         EN                                memo } from "r                        ingSpinner = memo(function LoadingSpinner({
  size = "default",
  label = "Loading...",
  showLabel = true,
}: {
  size?: "sm" | "default" | "lg"
  label?: string
  showLabel?: boolean
}) {
  const sizeClasses = {
    sm: "h-4 w-4",
    default: "h-8 w    default: "h-8 w    default: "h-8 w    default: "h-8 w me="flex flex-col items-center justify-center gap-3">
      <div className={`animate-s      <div className={r-2 b      <div classNorder-t-pr      <div className={`animateria-label={label}>
        <span className="sr-only">{label}</span>
      </div>
      {showLabel && (
        <p className="text-sm text-muted-foreground">{label}</p>
      )}
    </div>
  )
})

LoadingSpinner.displayName = "LoadingSpinner"
