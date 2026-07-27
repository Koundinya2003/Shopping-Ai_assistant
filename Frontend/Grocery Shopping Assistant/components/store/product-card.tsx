"use client"

import { useState, useCallback, memo } from "react"
import Image from "next/image"
import { discountPercent, type Product } from "@/lib/products"
import { useStore } from "./store-provider"

export const ProductCard = memo(function ProductCard({ product }: { product: Product }) {
  const { openDetails, addToCart, qtyOf, decrement } = useStore()
  const discount = discountPercent(product)
  const qty = qtyOf(product.id)
  const [added, setAdded] = useState(false)
  const [imgError, setImgError] = useState(false)

  const handleAdd = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    addToCart(product)
    setAdded(true)
    setTimeout(() => setAdded(false), 1200)
  }, [addToCart, product])

  const handleDecrement = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    decrement(product.id)
  }, [decrement, product.id])

  const showRating = product.rating > 0 && product.reviews > 0
  const hasDiscount = discount > 0 && product.mrp > product.price
  const imageSrc = !imgError && product.image ? product.image : "/placeholder.svg"

  return (
    <div className="group flex flex-col rounded-2xl border border-border bg-card p-2.5 transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 active:scale-[0.98] sm:p-3">
      {/* Product Image */}
      <button
        type="button"
        onClick={() => openDetails(product.id)}
        className="relative mb-2 aspect-square overflow-hidden rounded-xl bg-secondary/50"
        aria-label={`View ${product.name}`}
      >
        {hasDiscount && (
          <span className="absolute left-1.5 top-1.5 z-10 rounded-md bg-success px-1.5 py-0.5 text-[10px] font-bold text-success-foreground sm:left-2 sm:top-2">
            {discount}% OFF
          </span>
        )}
        <Image
          src={imageSrc}
          alt={product.name}
          fill
          sizes="(max-width: 640px) 50vw, (max-width: 1024px) 25vw, (max-width: 1280px) 20vw, 14vw"
          className="object-contain p-2 transition-transform duration-300 group-hover:scale-105"
          loading="lazy"
          onError={() => setImgError(true)}
        />
      </button>

      {/* Product Info */}
      <div className="flex flex-1 flex-col">
        {/* Product Name */}
        <button
          type="button"
          onClick={() => openDetails(product.id)}
          className="mb-0.5 line-clamp-2 text-left text-[13px] font-semibold leading-tight text-foreground transition-colors hover:text-primary sm:text-sm"
        >
          {product.name}
        </button>

        {/* Brand (secondary) */}
        <p className="mb-1 text-[11px] font-medium text-muted-foreground sm:text-xs">
          {product.brand}
        </p>

        {/* Weight / Variant */}
        <p className="mb-1.5 text-[11px] text-muted-foreground sm:text-xs">
          {product.unit}
        </p>

        {/* Rating (only if real data) */}
        {showRating && (
          <div className="mb-1.5 flex items-center gap-1">
            <svg className="h-3 w-3 text-primary" viewBox="0 0 20 20" fill="currentColor" aria-hidden>
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className="text-[11px] font-semibold text-foreground">
              {product.rating.toFixed(1)}
            </span>
            <span className="text-[11px] text-muted-foreground">
              ({product.reviews.toLocaleString()})
            </span>
          </div>
        )}

        {/* Price and Add Button */}
        <div className="mt-auto flex items-center justify-between gap-1.5">
          <div className="flex flex-col leading-none">
            <span className="text-base font-extrabold text-foreground sm:text-lg">
              ₹{product.price}
            </span>
            {hasDiscount && (
              <span className="text-[10px] line-through text-muted-foreground sm:text-xs">
                ₹{product.mrp}
              </span>
            )}
          </div>

          {/* Add Button / Quantity Stepper */}
          {qty === 0 ? (
            <button
              type="button"
              onClick={handleAdd}
              className={`relative flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground transition-all duration-200 hover:bg-primary-hover active:scale-90 sm:h-9 sm:w-9 ${
                added ? "scale-110" : ""
              }`}
              aria-label={`Add ${product.name} to cart`}
            >
              <span className="text-lg font-bold leading-none">+</span>
              {added && (
                <span className="absolute -top-8 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-md bg-success px-2 py-1 text-[10px] font-bold text-success-foreground animate-fade-in">
                  Added
                </span>
              )}
            </button>
          ) : (
            <div className="flex h-8 w-20 shrink-0 items-center justify-between rounded-full bg-primary text-primary-foreground sm:h-9 sm:w-24">
              <button
                type="button"
                onClick={handleDecrement}
                aria-label={`Remove one ${product.name}`}
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full transition-all duration-200 hover:bg-primary-hover active:scale-90 sm:h-9 sm:w-9"
              >
                <svg className="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden>
                  <path d="M5 10h10" strokeLinecap="round" />
                </svg>
              </button>
              <span className="min-w-[1.25rem] text-center text-sm font-bold tabular-nums">
                {qty}
              </span>
              <button
                type="button"
                onClick={handleAdd}
                aria-label={`Add one ${product.name}`}
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full transition-all duration-200 hover:bg-primary-hover active:scale-90 sm:h-9 sm:w-9"
              >
                <svg className="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden>
                  <path d="M10 5v10M5 10h10" strokeLinecap="round" />
                </svg>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
})

export default ProductCard