"use client"

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react"
import type { Product } from "@/lib/products"
import { fetchProducts, fetchRecommendations, type ApiProduct } from "@/lib/api"
import { mapApiProduct, mapApiRecommendation } from "@/lib/products"

type View = "home" | "details" | "cart"

type CartLine = { product: Product; qty: number }

type StoreContextValue = {
  view: View
  selectedId: string | null
  cart: CartLine[]
  cartCount: number
  cartTotal: number
  cartSavings: number
  openHome: () => void
  openDetails: (id: string) => void
  openCart: () => void
  addToCart: (product: Product, qty?: number) => void
  decrement: (id: string) => void
  removeFromCart: (id: string) => void
  qtyOf: (id: string) => number
  // API state
  products: Product[]
  aiPicks: Product[]
  productsLoading: boolean
  productsError: string | null
  recommendationsLoading: boolean
  recommendationsError: string | null
  // Recommendation drawer + loading animation
  showRecDrawer: boolean
  recDrawerProduct: Product | null
  showLoadingAnimation: boolean
  openRecDrawer: () => void
  dismissRecDrawer: () => void
  dismissedRecs: Set<string>
  dismissRecommendation: (productId: string) => void
  // Lookup
  getProductById: (id: string) => Product | undefined
}

const StoreContext = createContext<StoreContextValue | null>(null)

export function StoreProvider({ children }: { children: ReactNode }) {
  const [view, setView] = useState<View>("home")
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [cart, setCart] = useState<CartLine[]>([])

  // Product data
  const [rawProducts, setRawProducts] = useState<ApiProduct[]>([])
  const [productsLoading, setProductsLoading] = useState(true)
  const [productsError, setProductsError] = useState<string | null>(null)

  // Recommendation data
  const [recProducts, setRecProducts] = useState<Product[]>([])
  const [recommendationsLoading, setRecommendationsLoading] = useState(false)
  const [recommendationsError, setRecommendationsError] = useState<string | null>(null)

  // Recommendation drawer state
  const [showRecDrawer, setShowRecDrawer] = useState(false)
  const [recDrawerProduct, setRecDrawerProduct] = useState<Product | null>(null)
  const [showLoadingAnimation, setShowLoadingAnimation] = useState(false)
  const [dismissedRecs, setDismissedRecs] = useState<Set<string>>(new Set())

  // Derive frontend products
  const products = useMemo(
    () => rawProducts.map(mapApiProduct),
    [rawProducts],
  )

  // Build aiPicks by matching recommendations with our product list for images
  const aiPicks = useMemo(() => {
    return recProducts
  }, [recProducts])

  // Lookup product by id across both the main product list and AI picks.
  const getProductById = useCallback(
    (id: string) => products.find((p) => p.id === id) ?? aiPicks.find((p) => p.id === id),
    [products, aiPicks],
  )

  // Fetch products on mount
  useEffect(() => {
    let cancelled = false
    setProductsLoading(true)
    setProductsError(null)

    fetchProducts()
      .then((data) => {
        if (!cancelled) {
          setRawProducts(data)
          setProductsLoading(false)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setProductsError(err instanceof Error ? err.message : "Failed to load products")
          setProductsLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  // Fetch recommendations whenever cart changes (debounced)
  useEffect(() => {
    let cancelled = false

    const doFetch = () => {
      if (cancelled) return
      setRecommendationsLoading(true)
      setRecommendationsError(null)
      setShowLoadingAnimation(true)

      const cartNames = cart.map((l) => l.product.name)
      fetchRecommendations(cartNames)
        .then((recs) => {
          if (!cancelled) {
            const mapped: Product[] = recs.map((rec) => {
              const match = rawProducts.find(
                (p) => p.name.toLowerCase() === rec.product.toLowerCase(),
              )
              return mapApiRecommendation(rec, match)
            })
            setRecProducts(mapped)
            setRecommendationsLoading(false)
            setShowLoadingAnimation(false)
          }
        })
        .catch((err: unknown) => {
          if (!cancelled) {
            setRecommendationsError(
              err instanceof Error ? err.message : "Failed to load recommendations",
            )
            setRecommendationsLoading(false)
            setShowLoadingAnimation(false)
          }
        })
    }

    const timer = setTimeout(doFetch, 500)

    return () => {
      cancelled = true
      clearTimeout(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cart, rawProducts])

  const openHome = useCallback(() => setView("home"), [])
  const openCart = useCallback(() => setView("cart"), [])
  const openDetails = useCallback((id: string) => {
    setSelectedId(id)
    setView("details")
  }, [])

  const addToCart = useCallback((product: Product, qty = 1) => {
    setCart((prev) => {
      const existing = prev.find((l) => l.product.id === product.id)
      if (existing) {
        return prev.map((l) =>
          l.product.id === product.id ? { ...l, qty: l.qty + qty } : l,
        )
      }
      return [...prev, { product, qty }]
    })
  }, [])

  const openRecDrawer = useCallback(() => {
    if (recDrawerProduct || aiPicks[0]) {
      setShowRecDrawer(true)
    }
  }, [recDrawerProduct, aiPicks])

  const dismissRecDrawer = useCallback(() => {
    setShowRecDrawer(false)
    setRecDrawerProduct(null)
  }, [])

  const dismissRecommendation = useCallback((productId: string) => {
    setDismissedRecs((prev) => new Set(prev).add(productId))
  }, [])

  const decrement = useCallback((id: string) => {
    setCart((prev) =>
      prev
        .map((l) => (l.product.id === id ? { ...l, qty: l.qty - 1 } : l))
        .filter((l) => l.qty > 0),
    )
  }, [])

  const removeFromCart = useCallback((id: string) => {
    setCart((prev) => prev.filter((l) => l.product.id !== id))
  }, [])

  const qtyOf = useCallback(
    (id: string) => cart.find((l) => l.product.id === id)?.qty ?? 0,
    [cart],
  )

  const cartCount = useMemo(
    () => cart.reduce((sum, l) => sum + l.qty, 0),
    [cart],
  )
  const cartTotal = useMemo(
    () => cart.reduce((sum, l) => sum + l.product.price * l.qty, 0),
    [cart],
  )
  const cartSavings = useMemo(
    () => cart.reduce((sum, l) => sum + (l.product.mrp - l.product.price) * l.qty, 0),
    [cart],
  )

  const value: StoreContextValue = {
    view,
    selectedId,
    cart,
    cartCount,
    cartTotal,
    cartSavings,
    openHome,
    openDetails,
    openCart,
    addToCart,
    decrement,
    removeFromCart,
    qtyOf,
    products,
    aiPicks,
    productsLoading,
    productsError,
    recommendationsLoading,
    recommendationsError,
    showRecDrawer,
    recDrawerProduct,
    showLoadingAnimation,
    openRecDrawer,
    dismissRecDrawer,
    dismissedRecs,
    dismissRecommendation,
    getProductById,
  }

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>
}

export function useStore() {
  const ctx = useContext(StoreContext)
  if (!ctx) throw new Error("useStore must be used within StoreProvider")
  return ctx
}