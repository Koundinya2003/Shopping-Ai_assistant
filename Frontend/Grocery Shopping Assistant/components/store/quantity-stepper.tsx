"use client"

import { useCallback, useEffect, useRef, useState, memo } from "react"
import { MinusIcon, PlusIcon } from "@heroicons/react/24/solid"
import type { Product } from "@/lib/products"
import { useStore } from "./store-provider"

export const QuantityStepper = memo(function QuantityStepper({
  product,
  size = "sm",
  full = false,
}: {
  product: Product
  size?: "sm" | "lg"
  full?: boolean
}) {
  const { qtyOf, addToCart, decrement } = useStore()
  const qty = qtyOf(product.id)
  const [isAnimating, setIsAnimating] = useState(false)
  const prevQty = useRef(qty)
  const displayQty = useRef(qty)

  // Animate quantity changes
  useEffect(() => {
    if (prevQty.current !== qty) {
      setIsAnimating(true)
      displayQty.current = qty
      const timer = setTimeout(() => setIsAnimating(false), 200)
      prevQty.current = qty
      return () => clearTimeout(timer)
    }
  }, [qty])

  const handleDecrement = useCallback(() => {
    decrement(product.id)
  }, [decrement, product.id])

  const handleIncrement = useCallback(() => {
    addToCart(product)
  }, [addToCart, product])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "ArrowUp" || e.key === "ArrowRight") {
        e.preventDefault()
        handleIncrement()
      } else if (e.key === "ArrowDown" || e.key === "ArrowLeft") {
        e.preventDefault()
        handleDecrement()
      }
    },
    [handleIncrement, handleDecrement],
  )

  const isLarge = size === "lg"
  const dims = isLarge ? "h-11 text-base" : "h-8 text-sm"
  const iconBtn = isLarge ? "h-11 w-11" : "h-8 w-8"
  const iconSize = isLarge ? "icon-md" : "icon-sm"

  if (qty === 0) {
    return (
      <button
        type="button"
        onClick={handleIncrement}
        className={`${dims} ${full ? "w-full" : "px-4"} inline-flex items-center justify-center gap-1.5 rounded-full bg-primary text-primary-foreground transition-all duration-200 active:scale-95 hover:bg-primary-hover focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring add-btn-pulse touch-target`}
        aria-label={`Add ${product.name} to cart`}
      >
        <PlusIcon className={iconSize} aria-hidden />
        <span className="text-button">Add</span>
      </button>
    )
  }

  return (
    <div
      className={`${dims} ${full ? "w-full" : ""} inline-flex items-center justify-between gap-0.5 rounded-full bg-primary text-primary-foreground shadow-sm`}
      onKeyDown={handleKeyDown}
      role="group"
      aria-label={`Quantity selector for ${product.name}`}
    >
      <button
        type="button"
        onClick={handleDecrement}
        disabled={qty <= 1}
        aria-label={`Decrease quantity of ${product.name}`}
        className={`${iconBtn} inline-flex items-center justify-center rounded-full transition-all duration-200 active:scale-90 hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring touch-target`}
      >
        <MinusIcon className={iconSize} aria-hidden />
      </button>
      <span
        className={`min-w-[2rem] text-center tabular-nums text-button transition-transform ${isAnimating ? "animate-quantity-bump" : ""}`}
        aria-live="polite"
        aria-atomic="true"
      >
        {displayQty.current}
      </span>
      <button
        type="button"
        onClick={handleIncrement}
        aria-label={`Increase quantity of ${product.name}`}
        className={`${iconBtn} inline-flex items-center justify-center rounded-full transition-all duration-200 active:scale-90 hover:bg-primary-hover focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring touch-target`}
      >
        <PlusIcon className={iconSize} aria-hidden />
      </button>
    </div>
  )
})

export default QuantityStepper