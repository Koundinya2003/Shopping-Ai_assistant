"use client"

import { useState, useMemo, memo } from "react"
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  BoltIcon,
  ShoppingCartIcon,
  XMarkIcon,
} from "@heroicons/react/24/solid"
import { categories } from "@/lib/products"
import { ProductCard } from "./product-card"
import { useStore } from "./store-provider"

export const HomeScreen = memo(function HomeScreen() {
  const [active, setActive] = useState("all")
  const [query, setQuery] = useState("")
  const [searchFocused, setSearchFocused] = useState(false)
  const {
    products,
    productsLoading,
    productsError,
    openCart,
    cartCount,
  } = useStore()

  const filtered = useMemo(() => {
    return products.filter((p) => {
      const matchCat = active === "all" || p.category === active
      const matchQuery = query === "" || p.name.toLowerCase().includes(query.toLowerCase())
      return matchCat && matchQuery
    })
  }, [products, active, query])

  const hasSearch = query.length > 0

  return (
    <div className="pb-4">
      {/* Sticky Header */}
      <header className="sticky top-0 z-30 bg-background border-b border-border">
        <div className="px-4 pt-3 pb-2.5 lg:px-6">
          {/* Top row: brand + cart */}
          <div className="mb-2 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              {/* Brand Logo */}
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <svg className="h-5 w-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden>
                  <path d="M3 3h18v18H3z" />
                  <path d="M9 3v18M3 9h18" />
                </svg>
              </div>
              <div className="min-w-0">
                <h1 className="text-base font-bold text-foreground">Blinkit</h1>
              </div>
            </div>
            <button
              type="button"
              onClick={openCart}
              aria-label={`Open cart with ${cartCount} items`}
              className="cart-button relative flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-secondary transition-all duration-200 hover:bg-secondary-hover active:scale-90"
            >
              <ShoppingCartIcon className="icon-md text-foreground" aria-hidden />
              {cartCount > 0 && (
                <span className="absolute -right-0.5 -top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                  {cartCount}
                </span>
              )}
            </button>
          </div>

          {/* Delivery Info */}
          <div className="mb-2.5 flex items-center justify-between">
            <button
              type="button"
              className="flex items-center gap-1.5 text-left"
              aria-label="Delivery location"
            >
              <MapPinIcon className="icon-sm shrink-0 text-primary" aria-hidden />
              <div className="flex flex-col">
                <span className="text-caption font-semibold text-foreground">Delivering to Home</span>
              </div>
            </button>
          </div>

          {/* Search bar */}
          <div className="relative">
            <div className="search-input flex items-center gap-2">
              <MagnifyingGlassIcon
                className="icon-md shrink-0 text-muted-foreground"
                aria-hidden
              />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => setSearchFocused(true)}
                onBlur={() => setSearchFocused(false)}
                placeholder="Search for milk, bread, coffee…"
                aria-label="Search products"
                className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
              />
              {hasSearch && (
                <button
                  type="button"
                  onClick={() => setQuery("")}
                  className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground transition-colors hover:bg-border"
                  aria-label="Clear search"
                >
                  <XMarkIcon className="icon-sm" aria-hidden />
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Categories */}
      <section aria-label="Categories" className="px-4 pt-3 lg:px-6">
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
          {categories.map((c) => {
            const isActive = active === c.id
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => setActive(c.id)}
                className={`flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-semibold transition-all duration-200 active:scale-95 ${
                  isActive
                    ? "border-primary bg-primary text-primary-foreground shadow-card"
                    : "border-border bg-card text-foreground hover:border-primary/40 hover:bg-secondary"
                }`}
              >
                <span aria-hidden>{c.emoji}</span>
                {c.label}
              </button>
            )
          })}
        </div>
      </section>

      {/* Main Content Area */}
      <div className="lg:px-6">
        {/* Products Grid */}
        <section aria-labelledby="shelf-heading" className="px-4 pt-5 lg:px-0">
          <h2
            id="shelf-heading"
            className="text-heading mb-3"
          >
            {hasSearch ? "Search Results" : "Popular near you"}
          </h2>
          {productsLoading ? (
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-7">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14].map((i) => (
                <div
                  key={i}
                  className="flex flex-col rounded-2xl border border-border bg-card p-2.5 sm:p-3"
                >
                  <div className="mb-2 aspect-square rounded-xl bg-secondary/50 skeleton" />
                  <div className="mb-1.5 h-3 w-3/4 rounded skeleton" />
                  <div className="mb-1 h-2.5 w-1/2 rounded skeleton" />
                  <div className="mb-2 h-2.5 w-2/3 rounded skeleton" />
                  <div className="mt-auto flex items-center justify-between">
                    <div className="h-4 w-16 rounded skeleton" />
                    <div className="h-8 w-8 rounded-full skeleton sm:h-9 sm:w-9" />
                  </div>
                </div>
              ))}
            </div>
          ) : productsError ? (
            <div className="card-base border-dashed border-border py-10 text-center">
              <div className="mb-3 flex justify-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-error/10">
                  <svg className="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
              </div>
              <p className="text-label text-error mb-2">Failed to load products</p>
              <p className="text-caption text-muted-foreground mb-4">Please check your connection and try again</p>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="rounded-full bg-primary px-5 py-2 text-button font-bold text-primary-foreground transition-transform active:scale-95 hover:bg-primary-hover"
              >
                Retry
              </button>
            </div>
          ) : filtered.length === 0 ? (
            <div className="card-base border-dashed border-border py-10 text-center">
              <div className="mb-3 flex justify-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
                  <MagnifyingGlassIcon className="icon-lg text-muted-foreground" aria-hidden />
                </div>
              </div>
              <p className="text-label text-foreground mb-1">No products found</p>
              <p className="text-caption text-muted-foreground">Try adjusting your search or category filter</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-7">
              {filtered.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
})

export default HomeScreen