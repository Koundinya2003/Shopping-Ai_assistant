"use client"

import { useState, useEffect, useCallback } from "react"
import Image from "next/image"
import {
  SparklesIcon,
  XMarkIcon,
  ShoppingCartIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/solid"
import type { Product } from "@/lib/products"
import { useStore } from "./store-provider"
import { QuantityStepper } from "./quantity-stepper"
import { AIConfidenceIndicator } from "./ai-confidence-indicator"
import { AIReasoningCard } from "./ai-reasoning-card"
import { AIReviewSummary } from "./ai-review-summary"
import { AIRecommendationBadge } from "./ai-recommendation-badge"
import { AIInsightsPanel } from "./ai-insights-panel"
import { AIRecommendationFeedback } from "./ai-recommendation-feedback"

function RecommendationSkeleton() {
  return (
    <div className="animate-pulse space-y-3 p-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="rounded-2xl border border-border bg-card p-3">
          <div className="flex gap-3">
            <div className="h-20 w-20 shrink-0 rounded-xl bg-secondary" />
            <div className="flex-1 space-y-2">
              <div className="h-3 w-3/4 rounded bg-secondary" />
              <div className="h-2.5 w-1/2 rounded bg-secondary" />
              <div className="h-2.5 w-2/3 rounded bg-secondary" />
              <div className="h-8 w-20 rounded-full bg-secondary" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

function EmptyRecommendations() {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary">
        <SparklesIcon className="icon-xl text-muted-foreground" aria-hidden />
      </div>
      <h3 className="mb-2 text-base font-bold text-foreground">
        No strong complementary products were identified for this item.
      </h3>
      <p className="max-w-xs text-caption text-muted-foreground">
        Try adding different items to your cart to discover personalized recommendations
      </p>
    </div>
  )
}

function ErrorRecommendations({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-error/10">
        <svg className="icon-xl text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h3 className="mb-2 text-base font-bold text-foreground">
        Unable to load suggestions
      </h3>
      <p className="mb-4 max-w-xs text-caption text-muted-foreground">
        Something went wrong while fetching recommendations
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-button font-bold text-primary-foreground transition-all active:scale-95 hover:bg-primary-hover"
      >
        <ArrowPathIcon className="icon-sm" aria-hidden />
        Try Again
      </button>
    </div>
  )
}

export function CartRecommendationDrawer() {
  const {
    showRecDrawer,
    dismissRecDrawer,
    aiPicks,
    cart,
    recommendationsLoading,
    recommendationsError,
    addToCart,
    qtyOf,
    dismissRecommendation,
  } = useStore()

  const [isVisible, setIsVisible] = useState(false)
  const [isAnimating, setIsAnimating] = useState(false)

  // Handle drawer animation
  useEffect(() => {
    if (showRecDrawer) {
      setIsVisible(true)
      // Trigger animation after a brief delay
      const timer = setTimeout(() => setIsAnimating(true), 10)
      return () => clearTimeout(timer)
    } else {
      setIsAnimating(false)
      // Wait for animation to complete before hiding
      const timer = setTimeout(() => setIsVisible(false), 300)
      return () => clearTimeout(timer)
    }
  }, [showRecDrawer])

  const handleDismiss = useCallback(() => {
    dismissRecDrawer()
  }, [dismissRecDrawer])

  const handleDismissRec = useCallback((productId: string) => {
    dismissRecommendation(productId)
  }, [dismissRecommendation])

  const handleAddToCart = useCallback((product: Product) => {
    addToCart(product)
  }, [addToCart])

  const handleRetry = useCallback(() => {
    // Dismiss the drawer to reset state
    dismissRecDrawer()
    // The store will automatically refetch when the drawer is reopened
    // because the recommendationsLoading state will reset
  }, [dismissRecDrawer])

  if (!isVisible) return null

  // Filter out products already in cart and dismissed recommendations
  const cartProductIds = new Set(cart.map((item) => item.product.id))
  const availablePicks = aiPicks.filter(
    (pick) => !cartProductIds.has(pick.id)
  )

  return (
    <>
      {/* Backdrop */}
      <div
        className={`fixed inset-0 z-[60] bg-black/40 backdrop-blur-sm transition-opacity duration-300 ${
          isAnimating ? "opacity-100" : "opacity-0"
        }`}
        onClick={handleDismiss}
        aria-hidden="true"
      />

      {/* Drawer */}
      <div
        className={`fixed inset-x-0 bottom-0 z-[70] max-h-[85vh] overflow-y-auto rounded-t-3xl bg-background shadow-drawer transition-transform duration-300 ease-out lg:inset-x-auto lg:right-0 lg:top-0 lg:h-full lg:w-[420px] lg:rounded-l-3xl lg:rounded-r-none ${
          isAnimating ? "translate-y-0" : "translate-y-full lg:translate-y-0 lg:translate-x-full"
        }`}
        role="dialog"
        aria-modal="true"
        aria-label="Smart Suggestions"
      >
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-border bg-background/95 px-4 py-3 backdrop-blur">
            <div className="flex-1">
            <div className="flex items-center gap-2">
              <SparklesIcon className="icon-md text-primary" aria-hidden />
              <h2 className="text-base font-bold text-foreground">
                Smart Suggestions
              </h2>
            </div>
            <p className="mt-0.5 text-caption text-muted-foreground">
              Personalized picks to complete your cart
            </p>
          </div>
          <button
            type="button"
            onClick={handleDismiss}
            aria-label="Close suggestions"
            className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary transition-transform active:scale-90 hover:bg-secondary-hover ml-3"
          >
            <XMarkIcon className="icon-md text-foreground" aria-hidden />
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          {recommendationsLoading ? (
            <RecommendationSkeleton />
          ) : recommendationsError ? (
            <ErrorRecommendations onRetry={handleRetry} />
          ) : availablePicks.length === 0 ? (
            <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary">
                <SparklesIcon className="icon-xl text-muted-foreground" aria-hidden />
              </div>
              <h3 className="mb-2 text-base font-bold text-foreground">
                No strong complementary products were identified for this item.
              </h3>
              <p className="max-w-xs text-caption text-muted-foreground">
                Try adding different items to your cart to discover personalized recommendations
              </p>
            </div>
          ) : (
            <>
              {/* AI Insights Panel */}
              <AIInsightsPanel 
                insights={{
                  reviewsAnalyzed: 186,
                  productRelationships: 45,
                  shoppingPatterns: 128,
                  complementaryPurchases: 67,
                }}
              />
              
              <div className="space-y-3">
              {availablePicks.map((pick, index) => {
                const qty = qtyOf(pick.id)
                const discount = pick.mrp > pick.price
                  ? Math.round(((pick.mrp - pick.price) / pick.mrp) * 100)
                  : 0

                return (
                  <div
                    key={pick.id}
                    className="card-base overflow-hidden p-3 animate-scale-in"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex gap-3">
                      {/* Product Image */}
                      <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-xl bg-secondary">
                        <Image
                          src={pick.image || "/placeholder.svg"}
                          alt={pick.name}
                          fill
                          sizes="80px"
                          className="object-contain p-1.5"
                        />
                      </div>

                      {/* Product Info */}
                      <div className="flex-1 min-w-0">
                        <h3 className="text-label font-bold text-foreground text-balance line-clamp-2">
                          {pick.name}
                        </h3>
                        <p className="mt-0.5 text-caption text-muted-foreground">
                          {pick.unit}
                        </p>

                        {/* Price */}
                        <div className="mt-1 flex items-center gap-1.5">
                          <span className="text-label font-bold text-foreground">
                            ₹{pick.price}
                          </span>
                          {discount > 0 && (
                            <>
                              <span className="text-caption text-muted-foreground line-through">
                                ₹{pick.mrp}
                              </span>
                              <span className="badge-success text-[10px]">
                                {discount}% OFF
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                     {/* AI-Powered Recommendation Details */}
                     {pick.aiWhy && (
                       <div className="mt-2.5 space-y-2.5">
                         {/* Recommendation Badge */}
                         <AIRecommendationBadge 
                           type={pick.recommendationType || "frequently_bought_together"}
                           size="sm"
                         />

                         {/* Main AI Explanation */}
                         <div className="rounded-lg border border-primary/20 bg-accent/30 px-2.5 py-2">
                           <p className="text-caption leading-relaxed text-foreground">
                             {pick.aiWhy}
                           </p>
                         </div>

                         {/* Confidence Indicator */}
                         {pick.confidence && (
                           <AIConfidenceIndicator 
                             confidence={pick.confidence} 
                             size="sm"
                           />
                         )}

                         {/* AI Reasoning Card */}
                         {pick.aiReasoning && (
                           <AIReasoningCard reasoning={pick.aiReasoning} />
                         )}

                         {/* Review Summary */}
                         {pick.reviewSentiment && (
                           <AIReviewSummary
                             rating={pick.rating}
                             reviewCount={pick.reviews}
                             sentiment={pick.reviewSentiment}
                           />
                         )}

                         {/* Feedback */}
                         <AIRecommendationFeedback
                           productId={pick.id}
                           productName={pick.name}
                         />
                       </div>
                     )}

                     {/* Legacy Reason (fallback) */}
                     {!pick.aiWhy && pick.reason && (
                       <div className="mt-2.5 rounded-lg border border-primary/20 bg-accent/30 px-2.5 py-2">
                         <p className="text-caption leading-relaxed text-muted-foreground">
                           {pick.reason}
                         </p>
                       </div>
                     )}

                    {/* Actions */}
                    <div className="mt-2.5 flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => handleDismissRec(pick.id)}
                        aria-label={`Dismiss ${pick.name}`}
                        className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary transition-colors hover:bg-secondary-hover"
                      >
                        <XMarkIcon className="icon-sm text-muted-foreground" aria-hidden />
                      </button>

                      {qty === 0 ? (
                        <button
                          type="button"
                          onClick={() => handleAddToCart(pick)}
                          className="ml-auto flex items-center gap-1.5 rounded-full bg-primary px-4 py-2 text-button font-bold text-primary-foreground transition-all duration-200 active:scale-95 hover:bg-primary-hover"
                        >
                          <ShoppingCartIcon className="icon-sm" aria-hidden />
                          Add
                        </button>
                      ) : (
                        <div className="ml-auto">
                          <QuantityStepper product={pick} size="sm" />
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
            </>
          )}
        </div>
      </div>
    </>
  )
}
