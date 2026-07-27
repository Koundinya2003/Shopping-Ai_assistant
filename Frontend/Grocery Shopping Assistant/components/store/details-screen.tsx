"use client"

import Image from "next/image"
import {
  ArrowLeftIcon,
  SparklesIcon,
  CheckCircleIcon,
  XCircleIcon,
  ShoppingCartIcon,
} from "@heroicons/react/24/solid"
import { discountPercent } from "@/lib/products"
import { useStore } from "./store-provider"
import { Rating } from "./rating"
import { QuantityStepper } from "./quantity-stepper"

export function DetailsScreen() {
  const { selectedId, openHome, getProductById } = useStore()
  const product = selectedId ? getProductById(selectedId) : undefined

  if (!product) {
    return (
      <div className="p-6 text-center text-caption text-muted-foreground">
        Product not found.{" "}
        <button onClick={openHome} className="text-label font-semibold text-foreground underline">
          Go back
        </button>
      </div>
    )
  }

  const discount = discountPercent(product)

  return (
    <div className="pb-4">
      <div className="sticky top-0 z-10 flex items-center gap-3 bg-background/95 px-4 py-3 backdrop-blur">
        <button
          type="button"
          onClick={openHome}
          aria-label="Go back"
          className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-secondary transition-transform active:scale-90"
        >
          <ArrowLeftIcon className="icon-md text-foreground" aria-hidden />
        </button>
        <h1 className="truncate text-base font-bold text-foreground">
          {product.name}
        </h1>
      </div>

      {/* Image */}
      <div className="px-4">
        <div className="relative mx-auto aspect-square w-full max-w-xs overflow-hidden rounded-3xl bg-secondary">
          {product.aiRecommended && (
            <span className="badge-primary absolute left-3 top-3 z-10">
              <SparklesIcon className="icon-sm" aria-hidden />
              AI Recommended
            </span>
          )}
          <Image
            src={product.image || "/placeholder.svg"}
            alt={product.name}
            fill
            sizes="320px"
            className="object-contain p-6"
            priority
          />
        </div>
      </div>

      {/* Info */}
      <div className="px-4 pt-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-caption font-medium text-muted-foreground">{product.brand}</p>
            <h2 className="text-xl font-bold text-foreground text-balance">
              {product.name}
            </h2>
            <p className="text-caption text-muted-foreground">{product.unit}</p>
          </div>
          <Rating
            rating={product.rating}
            reviews={product.reviews}
            className="mt-1 shrink-0 rounded-full bg-secondary px-2.5 py-1"
          />
        </div>

        <div className="mt-3 flex items-center gap-2">
          <span className="text-price-lg">
            ₹{product.price}
          </span>
          {discount > 0 && (
            <>
              <span className="text-caption text-muted-foreground line-through">
                ₹{product.mrp}
              </span>
              <span className="badge-success">
                {discount}% OFF
              </span>
            </>
          )}
        </div>
      </div>

      {/* Why recommended */}
      {product.reason && (
        <section className="mx-4 mt-5 rounded-2xl border border-primary/30 bg-accent/50 p-4">
          <h3 className="mb-1.5 flex items-center gap-1.5 text-label font-bold text-foreground">
            <SparklesIcon className="icon-sm text-primary" aria-hidden />
            Why this was recommended
          </h3>
          <p className="text-caption leading-relaxed text-muted-foreground">
            {product.reason}
          </p>
        </section>
      )}

      {/* AI Review Summary */}
      {(product.pros || product.cons) && (
        <section className="px-4 pt-5">
          <h3 className="mb-3 flex items-center gap-1.5 text-heading font-bold text-foreground">
            <SparklesIcon className="icon-sm text-primary" aria-hidden />
            AI Review Summary
          </h3>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {product.pros && (
              <div className="card-base">
                <p className="text-label mb-2 font-bold text-success">Pros</p>
                <ul className="space-y-2">
                  {product.pros.map((pro) => (
                    <li key={pro} className="flex items-center gap-2 text-caption text-foreground">
                      <CheckCircleIcon className="icon-sm shrink-0 text-success" aria-hidden />
                      {pro}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {product.cons && (
              <div className="card-base">
                <p className="text-label mb-2 font-bold text-muted-foreground">Cons</p>
                <ul className="space-y-2">
                  {product.cons.map((con) => (
                    <li key={con} className="flex items-center gap-2 text-caption text-foreground">
                      <XCircleIcon className="icon-sm shrink-0 text-muted-foreground" aria-hidden />
                      {con}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  )
}

export function DetailsFooter() {
  const { selectedId, openCart, addToCart, qtyOf, getProductById } = useStore()
  const product = selectedId ? getProductById(selectedId) : undefined
  if (!product) return null
  const qty = qtyOf(product.id)

  return (
    <div className="border-t border-border bg-background p-3">
      {qty === 0 ? (
        <button
          type="button"
          onClick={() => addToCart(product)}
          className="flex w-full items-center justify-center gap-2 rounded-full bg-primary py-3.5 text-base font-bold text-primary-foreground transition-all active:scale-[0.98] hover:bg-primary-hover"
        >
          <ShoppingCartIcon className="icon-md" aria-hidden />
          Add to Cart · ₹{product.price}
        </button>
      ) : (
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <QuantityStepper product={product} size="lg" full />
          </div>
          <button
            type="button"
            onClick={openCart}
            className="flex-1 rounded-full bg-primary py-3 text-base font-bold text-primary-foreground transition-all active:scale-[0.98] hover:bg-primary-hover"
            aria-label={`Open cart with ${qty} ${product.name}`}
          >
            View Cart
          </button>
        </div>
      )}
    </div>
  )
}