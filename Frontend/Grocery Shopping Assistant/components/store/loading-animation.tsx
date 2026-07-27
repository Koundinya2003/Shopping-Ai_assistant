"use client"

import { useEffect, useState } from "react"
import { useStore } from "./store-provider"

const LOADING_MESSAGES = [
  {
    emoji: "🤖",
    text: "Analyzing shopping patterns...",
    subtext: "Understanding your cart",
  },
  {
    emoji: "📊",
    text: "Reading customer reviews...",
    subtext: "Learning from experiences",
  },
  {
    emoji: "✨",
    text: "Preparing recommendations...",
    subtext: "Almost there",
  },
]

export function LoadingAnimation() {
  const { showLoadingAnimation, recDrawerProduct } = useStore()
  const [messageIndex, setMessageIndex] = useState(0)

  // Cycle through loading messages
  useEffect(() => {
    if (!showLoadingAnimation) {
      setMessageIndex(0)
      return
    }

    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % LOADING_MESSAGES.length)
    }, 1500)

    return () => clearInterval(interval)
  }, [showLoadingAnimation])

  if (!showLoadingAnimation || !recDrawerProduct) return null

  const currentMessage = LOADING_MESSAGES[messageIndex]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm animate-fade-in">
      <div className="mx-4 w-full max-w-sm rounded-3xl bg-background p-8 text-center shadow-drawer animate-slide-up">
        {/* Animated emoji */}
        <div className="mb-4 text-5xl animate-bounce">
          {currentMessage.emoji}
        </div>

        {/* Progress dots */}
        <div className="mb-6 flex items-center justify-center gap-2">
          {LOADING_MESSAGES.map((_, idx) => (
            <div
              key={idx}
              className={`h-2 w-2 rounded-full transition-all duration-300 ${
                idx === messageIndex
                  ? "w-6 bg-primary"
                  : idx < messageIndex
                  ? "bg-primary/60"
                  : "bg-secondary"
              }`}
            />
          ))}
        </div>

        <div className="text-heading mb-2">
          {currentMessage.text}
        </div>
        <p className="text-caption text-muted-foreground">
          {currentMessage.subtext}
        </p>
      </div>
    </div>
  )
}
