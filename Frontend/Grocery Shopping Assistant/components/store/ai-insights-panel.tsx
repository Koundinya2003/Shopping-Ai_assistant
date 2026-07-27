"use client"

import { CheckCircleIcon } from "@heroicons/react/24/solid"
import type { AIInsights } from "@/lib/ai-transparency"

interface AIInsightsPanelProps {
  insights: AIInsights
}

export function AIInsightsPanel({ insights }: AIInsightsPanelProps) {
  const insightItems = [
    { label: "customer reviews", value: insights.reviewsAnalyzed },
    { label: "product relationships", value: insights.productRelationships },
    { label: "shopping patterns", value: insights.shoppingPatterns },
    { label: "complementary purchases", value: insights.complementaryPurchases },
  ]

  return (
    <div className="rounded-lg border border-border bg-secondary/20 p-3">
      <p className="text-caption font-semibold text-foreground mb-2">
        AI analyzed
      </p>
      <div className="space-y-1.5">
        {insightItems.map((item) => (
          <div key={item.label} className="flex items-center gap-2">
            <CheckCircleIcon className="icon-sm text-green-600 shrink-0" aria-hidden />
            <span className="text-caption text-muted-foreground">
              {item.value.toLocaleString()} {item.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}