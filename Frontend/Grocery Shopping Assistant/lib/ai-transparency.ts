/**
 * TypeScript interfaces for AI transparency features
 */

export type RecommendationType =
  | "frequently_bought_together"
  | "meal_companion"
  | "completes_your_order"
  | "popular_combination"
  | "recommended_from_reviews"
  | "perfect_pair"
  | "shopping_habit"

export type SentimentType = "positive" | "neutral" | "negative"

export interface ReviewSentiment {
  overall: SentimentType
  positivePercentage: number
  neutralPercentage: number
  negativePercentage: number
  mostLoved: string[]
  mostMentionedIssues: string[]
}

export interface AIReasoning {
  relationship: string
  customerReviewInsights: string
  commonUseCases: string[]
  confidence: number
  dataSources: string[]
}

export interface RecommendationFeedback {
  productId: string
  helpful: boolean
  timestamp: number
}

export interface AIInsights {
  reviewsAnalyzed: number
  productRelationships: number
  shoppingPatterns: number
  complementaryPurchases: number
}

/**
 * Get color class based on confidence score
 */
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 90) return "bg-green-500"
  if (confidence >= 70) return "bg-yellow-500"
  return "bg-red-500"
}

/**
 * Get text color class based on confidence score
 */
export function getConfidenceTextColor(confidence: number): string {
  if (confidence >= 90) return "text-green-600"
  if (confidence >= 70) return "text-yellow-600"
  return "text-red-600"
}

/**
 * Format recommendation type for display
 */
export function formatRecommendationType(type: RecommendationType): string {
  const labels: Record<RecommendationType, string> = {
    frequently_bought_together: "Frequently Bought Together",
    meal_companion: "Meal Companion",
    completes_your_order: "Completes Your Order",
    popular_combination: "Popular Combination",
    recommended_from_reviews: "Recommended from Reviews",
    perfect_pair: "Perfect Pair",
    shopping_habit: "Shopping Habit",
  }
  return labels[type] || "Recommended"
}

/**
 * Store feedback in localStorage
 */
export function storeFeedback(feedback: RecommendationFeedback): void {
  try {
    const existing = getStoredFeedback()
    existing.push(feedback)
    localStorage.setItem("recommendation_feedback", JSON.stringify(existing))
  } catch (error) {
    console.error("Failed to store feedback:", error)
  }
}

/**
 * Get all stored feedback
 */
export function getStoredFeedback(): RecommendationFeedback[] {
  try {
    const stored = localStorage.getItem("recommendation_feedback")
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.error("Failed to get feedback:", error)
    return []
  }
}

/**
 * Check if user has already provided feedback for a product
 */
export function hasUserFeedback(productId: string): boolean {
  const feedback = getStoredFeedback()
  return feedback.some((f) => f.productId === productId)
}