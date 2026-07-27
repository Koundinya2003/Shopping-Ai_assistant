"use client"

import { SparklesIcon } from "@heroicons/react/24/solid"
import { formatRecommendationType, type RecommendationType } from "@/lib/ai-transparency"

interface AIRecommendationBadgeProps {
  type: RecommendationType
  size?: "sm" | "md"
}

export function AIRecommendationBadge({
  type,
  size = "md",
}: AIRecommendationBadgeProps) {
  const label = formatRecommendationType(type)

  const sizeClasses = {
    sm: "text-[10px] px-2 py-0.5",
    md: "text-xs px-2.5 py-1",
  }

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full bg-primary/10 text-primary font-semibold ${sizeClasses[size]}`}
    >
      <SparklesIcon className="icon-xs" aria-hidden />
      {label}
    </span>
  )
}