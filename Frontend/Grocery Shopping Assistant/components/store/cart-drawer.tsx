"use client"

import { useEffect, useRef, useCallback } from "react"
import Image from "next/image"
import {
  ArrowLeftIcon,
  SparklesIcon,
  TrashIcon,
  ShoppingBagIcon,
} from "@heroicons/react/24/solid"
import type { Product } from "@/lib/products"
import { useStore } from "./store-provider"
import { QuantityStepper } from "./quantity-stepper"
import { CartRecommendationDrawer } from "./cart-recommendation-drawer"

function computeFees(cartTotal: number) {
  const deliveryFee = cartTotal > 0 && cartTotal < 199 ? 25 : 0
  return { deliveryFee, grandTotal: cartTotal + deliveryFee }
}

export function CartDrawer() {
  const {
    cart,
    cartTotal,
    cartSavings,
    openHome,
    removeFromCart,
    openCart,
    view,
    aiPicks,
    recommendationsLoading,
    recommendationsError,
    openRecDrawer,
    dismissedRecs,
  } = useStore()
  const { deliveryFee, grandTotal } = computeFees(cartTotal)
  const drawerRef = useRef<HTMLDivElement>(null)

  // Handle escape key
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape" && view === "cart") {
        openHome()
      }
    },
    [view, openHome],
  )

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [handleKeyDown])

  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (view === "cart") {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = ""
    }
    return () => {
      document.body.style.overflow = ""
    }
  }, [view])

  if (view !== "cart") return null

  // Filter out dismissed and cart items
  const availableRecommendations = aiPicks.filter(
    (pick) => !dismissedRecs.has(pick.id) && !cart.some((item) => item.product.id === pick.id)
  )

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm animate-fade-in"
        onClick={openHome}
        aria-hidden="true"
      />

      {/* Drawer */}
      <div
        ref={drawerRef}
        className="fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col bg-background shadow-drawer animate-slide-in-right lg:animate-slide-in-right"
        role="dialog"
        aria-modal="true"
        aria-label="Shopping cart"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={openHome}
              aria-label="Close cart"
              className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-secondary transition-all active:scale-90 hover:bg-secondary-hover"
            >
              <ArrowLeftIcon className="icon-md text-foreground" aria-hidden />
            </button>
            <h2 className="text-base font-bold text-foreground">Your Cart</h2>
            {cart.length > 0 && (
              <span className="text-caption text-muted-foreground">
                ({cart.length} {cart.length === 1 ? "item" : "items"})
              </span>
            )}
          </div>
        </div>

        {/* Cart Content */}
        <div className="flex-1 overflow-y-auto">
          {cart.length === 0 ? (
            <EmptyCart />
          ) : (
            <div className="p-4">
              {/* Cart Items */}
              <ul className="space-y-3">
                {cart.map(({ product, qty }) => (
                  <CartItem
                    key={product.id}
                    product={product}
                    qty={qty}
                    onRemove={() => removeFromCart(product.id)}
                  />
                ))}
              </ul>

              {/* Smart Suggestions Section */}
              {!recommendationsLoading && !recommendationsError && availableRecommendations.length > 0 && (
                <button
                  type="button"
                  onClick={openRecDrawer}
                  className="mt-4 w-full rounded-2xl border border-primary/30 bg-gradient-to-br from-primary/5 to-accent/5 p-4 text-left transition-all duration-200 hover:border-primary/50 hover:shadow-md active:scale-[0.98]"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <SparklesIcon className="icon-md text-primary" aria-hidden />
                    <h3 className="text-label font-bold text-foreground">
                      Complete your basket
                    </h3>
                  </div>
                  <p className="text-caption text-muted-foreground">
                    {availableRecommendations.length} suggestion{availableRecommendations.length !== 1 ? 's' : ''} based on your cart
                  </p>
                </button>
              )}

              {/* Bill Summary */}
              <div className="mt-4 rounded-2xl border border-border bg-card p-4">
                <h3 className="text-label mb-3 font-bold text-foreground">
                  Bill Details
                </h3>
                <dl className="space-y-2.5 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">Item total</dt>
                    <dd className="font-semibold text-foreground">
                      ₹{cartTotal}
                    </dd>
                  </div>
                  {deliveryFee === 0 ? (
                    <div className="flex justify-between">
                      <dt className="text-muted-foreground">Delivery fee</dt>
                      <dd className="font-semibold text-success">FREE</dd>
                    </div>
                  ) : (
                    <div className="flex justify-between">
                      <dt className="text-muted-foreground">Delivery fee</dt>
                      <dd className="font-semibold text-foreground">
                        ₹{deliveryFee}
                      </dd>
                    </div>
                  )}
                  <div className="mt-3 flex justify-between border-t border-border pt-3 text-base">
                    <dt className="font-bold text-foreground">To pay</dt>
                    <dd className="font-bold text-foreground">
                      ₹{grandTotal}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          )}
        </div>

        {/* Checkout Footer */}
        {cart.length > 0 && (
          <div className="border-t border-border bg-background p-4">
            <button
              type="button"
              className="flex w-full items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-base font-bold text-primary-foreground transition-all active:scale-[0.98] hover:bg-primary-hover"
            >
              <span>Proceed to Checkout</span>
              <ArrowLeftIcon className="icon-md rotate-180" aria-hidden />
            </button>
            <p className="mt-2 text-center text-caption text-muted-foreground">
              ₹{grandTotal} total
            </p>
          </div>
        )}

        {/* Recommendation Drawer */}
        <CartRecommendationDrawer />
      </div>
    </>
  )
}

function CartItem({
  product,
  qty,
  onRemove,
}: {
  product: Product
  qty: number
  onRemove: () => void
}) {
  return (
    <li
      className="card-base flex gap-3 p-3"
    >
      {/* Product Image */}
      <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-xl bg-secondary">
        <Image
          src={product.image || "/placeholder.svg"}
          alt={product.name}
          fill
          sizes="80px"
          className="object-contain p-2"
        />
      </div>

      {/* Product Details */}
      <div className="flex flex-1 flex-col justify-between">
        <div>
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1">
              <h4 className="text-label font-semibold text-foreground line-clamp-2">
                {product.name}
              </h4>
              <p className="mt-0.5 text-caption text-muted-foreground">
                {product.unit}
              </p>
            </div>
            <button
              type="button"
              onClick={onRemove}
              aria-label={`Remove ${product.name} from cart`}
              className="shrink-0 rounded-full p-1.5 text-muted-foreground transition-colors hover:bg-error/10 hover:text-destructive"
            >
              <TrashIcon className="icon-sm" aria-hidden />
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <p className="text-base font-bold text-foreground">
            ₹{product.price * qty}
          </p>
          <QuantityStepper product={product} size="sm" />
        </div>
      </div>
    </li>
  )
}

function EmptyCart() {
  const { openHome } = useStore()

  return (
    <div className="flex flex-col items-center justify-center px-6 py-20 text-center">
      <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-secondary">
        <ShoppingBagIcon className="icon-xl text-muted-foreground" aria-hidden />
      </div>
      <h3 className="mb-2 text-lg font-bold text-foreground">
        Your cart is empty
      </h3>
      <p className="mb-6 max-w-xs text-caption text-muted-foreground">
        Looks like you haven't added anything to your cart yet. Start
        shopping to fill it up!
      </p>
      <button
        type="button"
        onClick={openHome}
        className="rounded-full bg-primary px-8 py-3 text-button font-bold text-primary-foreground transition-all active:scale-95 hover:bg-primary-hover"
      >
        Continue Shopping
      </button>
    </div>
  )
}