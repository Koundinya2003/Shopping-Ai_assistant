"use client"

import { StoreProvider, useStore } from "./store-provider"
import { HomeScreen } from "./home-screen"
import { DetailsScreen, DetailsFooter } from "./details-screen"
import { CartDrawer } from "./cart-drawer"
import { BottomNav } from "./bottom-nav"
import { LoadingAnimation } from "./loading-animation"

function Screens() {
  const { view } = useStore()
  return (
    <>
      <main
        key={view}
        className="flex-1 overflow-y-auto"
      >
        <div className="mx-auto w-full max-w-7xl">
          {view === "home" && <HomeScreen />}
          {view === "details" && <DetailsScreen />}
        </div>
      </main>
      {view === "details" && <DetailsFooter />}
      <BottomNav />
      <CartDrawer />
      <LoadingAnimation />
    </>
  )
}

export function AppShell() {
  return (
    <StoreProvider>
      <div className="flex h-svh w-full flex-col overflow-hidden bg-background">
        <Screens />
      </div>
    </StoreProvider>
  )
}