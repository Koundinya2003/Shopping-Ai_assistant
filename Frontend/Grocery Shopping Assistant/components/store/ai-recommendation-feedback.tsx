"use client"

import { useState } from "react"
import { HandThumbUpIcon, HandThumbDownIcon } from "@heroicons/react/24/solid"
import { storeFeedback, hasUserFeedback, type RecommendationFeedback } from "@/lib/ai-transparency"

interface AIRecommendationFeedbackProps {
  productId: string
  productName: string
  onFeedbackSubmit?: (feedback: RecommendationFeedback) => void
}

export function AIRecommendationFeedback({
  productId,
  productName,
  onFeedbackSubmit,
}: AIRecommendationFeedbackProps) {
  const [feedbackGiven, setFeedbackGiven] = useState(false)
  const [feedbackType, setFeedbackType] = useState<"helpful" | "not_relevant" | null>(null)

  const hasFeedback = hasUserFeedback(productId)

  const handleFeedback = (helpful: boolean) => {
    if (feedbackGiven || hasFeedback) return

    const feedback: RecommendationFeedback = {
      productId,
      helpful,
      timestamp: Date.now(),
    }

    storeFeedback(feedback)
    setFeedbackGiven(true)
    setFeedbackType(helpful ? "helpful" : "not_relevant")
    onFeedbackSubmit?.(feedback)
  }

  if (hasFeedback || feedbackGiven) {
    return (
      <div className="flex items-center gap-1.5 text-caption text-muted-foreground">
        {feedbackType === "helpful" ? (
          <>
            <HandThumbUpIcon className="icon-sm text-green-600" aria-hidden />
            <span>Thanks for your feedback!</span>
          </>
        ) : (
          <>
            <HandThumbDownIcon className="icon-sm text-muted-foreground" aria-hidden />
            <span>We'll improve our recommendations</span>
          </>
        )}
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-caption text-muted-foreground">Was this helpful?</span>
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={() => handleFeedback(true)}
          className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-secondary transition-colors hover:bg-secondary-hover"
          aria-label={`Mark ${productName} as helpful`}
          title="Helpful"
        >
          <HandThumbUpIcon className="icon-sm text-muted-foreground" aria-hidden />
        </button>
        <button
          type="button"
          onClick={() => handleFeedback(false)}
          className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-secondary transition-colors hover:bg-secondary-hover"
          aria-label={`Mark ${productName} as not relevant`}
          title="Not Relevant"
        >
          <HandThumbDownIcon className="icon-sm text-muted-foreground" aria-hidden />
        </button>
      </div>
    </div>
  )
}