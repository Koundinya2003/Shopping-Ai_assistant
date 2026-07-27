"use client"

import {
  HomeIcon,
  Squares2X2Icon,
  ShoppingCartIcon,
  UserIcon,
} from "@heroicons/react/24/outline"
import {
  HomeIcon as HomeSolid,
  ShoppingCartIcon as CartSolid,
} from "@heroicons/react/24/solid"
import { useStore } from "./store-provider"

export function BottomNav() {
  const { view, openHome, openCart, cartCount } = useStore()
  const activeHome = view === "home" || view === "details"
  const activeCart = view === "cart"

  return (
    <nav
      aria-label="Primary"
      className="sticky bottom-0 z-20 border-t border-border bg-background/95 backdrop-blur lg:hidden"
    >
      <ul className="mx-auto flex max-w-md items-stretch justify-around px-2 py-1.5">
        <li className="flex-1">
          <button
            type="button"
            onClick={openHome}
            className={`flex w-full flex-col items-center gap-0.5 rounded-xl py-1.5 text-caption font-semibold transition-colors ${activeHome ? "text-foreground" : "text-muted-foreground"}`}
          >
            {activeHome ? (
              <HomeSolid className="icon-lg text-primary" aria-hidden />
            ) : (
              <HomeIcon className="icon-lg" aria-hidden />
            )}
            Home
          </button>
        </li>
        <li className="flex-1">
          <button
            type="button"
            className="flex w-full flex-col items-center gap-0.5 rounded-xl py-1.5 text-caption font-semibold text-muted-foreground"
          >
            <Squares2X2Icon className="icon-lg" aria-hidden />
            Categories
          </button>
        </li>
        <li className="flex-1">
          <button
            type="button"
            onClick={openCart}
            className={`cart-button relative flex w-full flex-col items-center gap-0.5 rounded-xl py-1.5 text-caption font-semibold transition-colors ${activeCart ? "text-foreground" : "text-muted-foreground"}`}
            aria-label={`Open cart with ${cartCount} items`}
          >
            {activeCart ? (
              <CartSolid className="icon-lg text-primary" aria-hidden />
            ) : (
              <ShoppingCartIcon className="icon-lg" aria-hidden />
            )}
            {cartCount > 0 && (
              <span className="absolute -right-0.5 -top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                {cartCount}
              </span>
            )}
            Cart
          </button>
        </li>
        <li className="flex-1">
          <button
            type="button"
            className="flex w-full flex-col items-center gap-0.5 rounded-xl py-1.5 text-caption font-semibold text-muted-foreground"
          >
            <UserIcon className="icon-lg" aria-hidden />
            Account
          </button>
        </li>
      </ul>
    </nav>
  )
}