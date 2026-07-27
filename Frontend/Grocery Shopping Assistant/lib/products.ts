import type { ApiProduct, ApiRecommendation } from "./api"
import type { RecommendationType, AIReasoning, ReviewSentiment } from "./ai-transparency"

export type Product = {
  id: string
  name: string
  brand: string
  unit: string
  price: number
  mrp: number
  rating: number
  reviews: number
  image: string
  category: string
  aiRecommended?: boolean
  reason?: string
  // AI-powered fields
  aiWhy?: string
  confidence?: number
  when?: string
  bestFor?: string
  reviewSummary?: string
  pros?: string[]
  cons?: string[]
  recommendationType?: RecommendationType
  aiReasoning?: AIReasoning
  reviewSentiment?: ReviewSentiment
}

export const categories = [
  { id: "all", label: "All", emoji: "🛒" },
  { id: "fruits", label: "Fruits & Veg", emoji: "🥬" },
  { id: "dairy", label: "Dairy & Eggs", emoji: "🥚" },
  { id: "bakery", label: "Bakery", emoji: "🍞" },
  { id: "snacks", label: "Snacks", emoji: "🍿" },
  { id: "beverages", label: "Beverages", emoji: "☕" },
  { id: "pantry", label: "Pantry", emoji: "🧂" },
]

/**
 * Simple brand derivation based on product name.
 */
const brandMap: Record<string, string> = {
  "milk": "Amul",
  "eggs": "Fresh Eggoz",
  "bread": "Harvest Gold",
  "bananas": "Fresh",
  "tomatoes": "Fresh",
  "greek yogurt": "Epigamia",
  "dark chocolate": "Lindt",
  "chips": "Lay's",
  "instant coffee": "Nescafe",
  "schezwan sauce": "Maggie",
  "paneer": "Amul",
  "butter": "Amul",
  "cheese": "Amul",
  "curd": "Amul",
  "mixed nuts": "Happilo",
  "green tea": "Tata Tea",
  "detergent": "Surf Excel",
  "dish soap": "Vim",
  "toothpaste": "Colgate",
  "shampoo": "Dove",
  "soap": "Lifebuoy",
  "rice": "India Gate",
  "flour": "Aashirvaad",
  "salt": "Tata Salt",
  "sugar": "Madhur",
  "cooking oil": "Fortune",
  "pasta": "Barilla",
  "ketchup": "Kissan",
  "juice": "Real",
}

function deriveBrand(name: string): string {
  const lower = name.toLowerCase()
  for (const [key, brand] of Object.entries(brandMap)) {
    if (lower.includes(key)) return brand
  }
  return "Blinkit"
}

/**
 * Map the backend API product to the frontend Product type.
 */
export function mapApiProduct(api: ApiProduct): Product {
  const mrp =
    api.discount > 0
      ? Math.round(api.price / (1 - api.discount / 100))
      : api.price

  return {
    id: String(api.id),
    name: api.name,
    brand: deriveBrand(api.name),
    unit: api.unit || "",
    price: api.price,
    mrp,
    rating: api.rating,
    reviews: api.reviews_count,
    image: api.image_url || "/placeholder.svg",
    category: api.category.toLowerCase(),
  }
}

/**
 * Map a backend ApiRecommendation to a frontend Product (for AI Picks).
 */
export function mapApiRecommendation(
  rec: ApiRecommendation,
  apiProduct?: ApiProduct,
): Product {
  const mrp =
    rec.discount > 0
      ? Math.round(rec.price / (1 - rec.discount / 100))
      : rec.price

  // Determine recommendation type based on available data
  const recommendationType: RecommendationType = (rec.recommendation_type as RecommendationType) || "frequently_bought_together"

  // Build AI reasoning from available fields
  const aiReasoning: AIReasoning | undefined = rec.why ? {
    relationship: rec.why,
    customerReviewInsights: rec.review_summary || "Based on customer purchase patterns",
    commonUseCases: rec.best_for ? [rec.best_for] : [],
    confidence: rec.confidence || 75,
    dataSources: [
      "Customer Reviews",
      "Product Relationships",
      "Shopping Patterns",
    ],
  } : undefined

  // Build review sentiment from available data
  const reviewSentiment: ReviewSentiment | undefined = rec.review_summary ? {
    overall: "positive",
    positivePercentage: 75,
    neutralPercentage: 15,
    negativePercentage: 10,
    mostLoved: rec.pros || [],
    mostMentionedIssues: rec.cons || [],
  } : undefined

  return {
    id: apiProduct ? String(apiProduct.id) : rec.product.toLowerCase().replace(/\s+/g, "-"),
    name: rec.product,
    brand: apiProduct ? deriveBrand(apiProduct.name) : deriveBrand(rec.product),
    unit: apiProduct?.unit || "",
    price: rec.price,
    mrp,
    rating: rec.rating,
    reviews: 0,
    image: apiProduct?.image_url || "/placeholder.svg",
    category: apiProduct?.category?.toLowerCase() || "",
    aiRecommended: true,
    reason: rec.why_recommended || rec.recommendation_reason || undefined,
    // AI-powered fields
    aiWhy: rec.why || undefined,
    confidence: rec.confidence || undefined,
    when: rec.when || undefined,
    bestFor: rec.best_for || undefined,
    reviewSummary: rec.review_summary || undefined,
    pros: rec.pros || undefined,
    cons: rec.cons || undefined,
    recommendationType,
    aiReasoning,
    reviewSentiment,
  }
}

export function discountPercent(product: Product) {
  return Math.round(((product.mrp - product.price) / product.mrp) * 100)
}