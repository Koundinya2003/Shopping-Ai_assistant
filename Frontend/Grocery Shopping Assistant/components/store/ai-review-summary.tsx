"use client"

import { StarIcon } from "@heroicons/react/24/solid"
import type { ReviewSentiment } from "@/lib/ai-transparency"

interface AIReviewSummaryProps {
  rating: number
  reviewCount: number
  sentiment: ReviewSentiment
}

export function AIReviewSummary({
  rating,
  reviewCount,
  sentiment,
}: AIReviewSummaryProps) {
  const getSentimentColor = (type: string) => {
    switch (type) {
      case "positive":
        return "text-green-600"
      case "neutral":
        return "text-yellow-600"
      case "negative":
        return "text-red-600"
      default:
        return "text-muted-foreground"
    }
  }

  return (
    <div className="mt-2.5 space-y-2.5">
      {/* Rating Overview */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1">
          <StarIcon className="icon-sm text-yellow-500" aria-hidden />
          <span className="text-label font-bold text-foreground">
            {rating.toFixed(1)}
          </span>
        </div>
        <span className="text-caption text-muted-foreground">
          ({reviewCount} reviews)
        </span>
      </div>

      {/* Sentiment Breakdown */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-caption text-muted-foreground">Positive</span>
          <span className={`text-caption font-semibold ${getSentimentColor("positive")}`}>
            {sentiment.positivePercentage}%
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-caption text-muted-foreground">Neutral</span>
          <span className={`text-caption font-semibold ${getSentimentColor("neutral")}`}>
            {sentiment.neutralPercentage}%
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-caption text-muted-foreground">Negative</span>
          <span className={`text-caption font-semibold ${getSentimentColor("negative")}`}>
            {sentiment.negativePercentage}%
          </span>
        </div>
      </div>

      {/* Most Loved */}
      {sentiment.mostLoved.length > 0 && (
        <div className="space-y-1">
          <p className="text-caption font-semibold text-foreground">Most Loved</p>
          <ul className="space-y-0.5">
            {sentiment.mostLoved.map((item, index) => (
              <li
                key={index}
                className="text-caption text-muted-foreground list-disc pl-4"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Most Mentioned Issues */}
      {sentiment.mostMentionedIssues.length > 0 && (
        <div className="space-y-1">
          <p className="text-caption font-semibold text-foreground">
            Most Mentioned Issues
          </p>
          <ul className="space-y-0.5">
            {sentiment.mostMentionedIssues.map((item, index) => (
              <li
                key={index}
                className="text-caption text-muted-foreground list-disc pl-4"
              >
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}