"use client"

import { useState } from "react"
import { ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/24/solid"
import type { AIReasoning } from "@/lib/ai-transparency"

interface AIReasoningCardProps {
  reasoning: AIReasoning
}

export function AIReasoningCard({ reasoning }: AIReasoningCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="mt-2.5 space-y-2">
      {/* Expandable Header */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between rounded-lg border border-primary/20 bg-accent/30 px-2.5 py-2 transition-colors hover:bg-accent/50"
        aria-expanded={isExpanded}
      >
        <span className="text-caption font-semibold text-foreground">
          Why did AI recommend this?
        </span>
        {isExpanded ? (
          <ChevronUpIcon className="icon-sm text-muted-foreground" aria-hidden />
        ) : (
          <ChevronDownIcon className="icon-sm text-muted-foreground" aria-hidden />
        )}
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="space-y-3 rounded-lg border border-border bg-secondary/30 p-3 animate-in">
          {/* Shopping Relationship */}
          <div>
            <h4 className="text-caption font-semibold text-foreground mb-1">
              Relationship
            </h4>
            <p className="text-caption text-muted-foreground leading-relaxed">
              {reasoning.relationship}
            </p>
          </div>

          {/* Customer Review Insights */}
          <div>
            <h4 className="text-caption font-semibold text-foreground mb-1">
              Customer Reviews
            </h4>
            <p className="text-caption text-muted-foreground leading-relaxed">
              {reasoning.customerReviewInsights}
            </p>
          </div>

          {/* Common Use Cases */}
          {reasoning.commonUseCases.length > 0 && (
            <div>
              <h4 className="text-caption font-semibold text-foreground mb-1">
                Common Use Cases
              </h4>
              <ul className="space-y-1">
                {reasoning.commonUseCases.map((useCase, index) => (
                  <li
                    key={index}
                    className="text-caption text-muted-foreground list-disc pl-4"
                  >
                    {useCase}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Confidence Score */}
          <div>
            <h4 className="text-caption font-semibold text-foreground mb-1">
              Confidence
            </h4>
            <p className="text-caption text-muted-foreground">
              {reasoning.confidence}%
            </p>
          </div>

          {/* Data Sources */}
          <div>
            <h4 className="text-caption font-semibold text-foreground mb-1">
              Sources
            </h4>
            <ul className="space-y-1">
              {reasoning.dataSources.map((source, index) => (
                <li
                  key={index}
                  className="text-caption text-muted-foreground flex items-center gap-1.5"
                >
                  <span className="text-green-600">✓</span>
                  {source}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}