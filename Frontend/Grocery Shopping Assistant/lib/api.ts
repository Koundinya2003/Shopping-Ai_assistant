/**
 * API service layer for all backend communication.
 * Reads the backend base URL from NEXT_PUBLIC_API_URL environment variable.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export type ApiProduct = {
  id: number
  name: string
  category: string
  price: number
  rating: number
  discount: number
  image_url: string | null
  unit: string
  reviews_count: number
}

export type ApiRecommendation = {
  product: string
  rating: number
  price: number
  discount: number
  // AI-powered fields
  confidence: number | null
  why: string | null
  when: string | null
  best_for: string | null
  review_summary: string | null
  pros: string[] | null
  cons: string[] | null
  recommendation_type: string | null
  // Legacy fields (kept for backward compatibility)
  why_recommended: string | null
  summary: string | null
  recommendation_reason: string | null
}

export type ApiRecommendationRequest = {
  cart: string[]
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  })

  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error")
    throw new Error(`API ${res.status}: ${text}`)
  }

  return res.json() as Promise<T>
}

export async function fetchProducts(): Promise<ApiProduct[]> {
  return request<ApiProduct[]>("/products")
}

export async function fetchRecommendations(
  cart: string[],
): Promise<ApiRecommendation[]> {
  return request<ApiRecommendation[]>("/recommendations", {
    method: "POST",
    body: JSON.stringify({ cart } satisfies ApiRecommendationRequest),
  })
}