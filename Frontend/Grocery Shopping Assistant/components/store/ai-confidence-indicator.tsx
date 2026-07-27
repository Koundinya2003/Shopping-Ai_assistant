"use client"

import { getConfidenceColor, getConfidenceTextColor } from "@/lib/ai-transparency"

interface AIConfidenceIndicatorProps {
  confidence: number
  showLabel?: boolean
  size?: "sm" | "md" | "lg"
}

export function AIConfidenceIndicator({
  confidence,
  showLabel = true,
  size = "md",
}: AIConfidenceIndicatorProps) {
  const colorClass = getConfidenceColor(confidence)
  const textColorClass = getConfidenceTextColor(confidence)

  const sizeClasses = {
    sm: "h-1.5",
    md: "h-2",
    lg: "h-2.5",
  }

  const textSizeClasses = {
    sm: "text-xs",
    md: "text-sm",
    lg: "text-base",
  }

  return (
    <div className="space-y-1">
      {showLabel && (
        <div className="flex items-center justify-between">
          <span className="text-caption font-semibold text-foreground">
            AI Confidence
          </span>
          <span className={`text-caption font-bold ${textColorClass}`}>
            {confidence}%
          </span>
        </div>
      )}
      <div className={`w-full rounded-full bg-secondary ${sizeClasses[size]}`}>
        <div
          className={`${sizeClasses[size]} rounded-full transition-all duration-500 ${colorClass}`}
          style={{ width: `${confidence}%` }}
          role="progressbar"
          aria-valuenow={confidence}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`AI confidence: ${confidence}%`}
        />
      </div>
    </div>
  )
}