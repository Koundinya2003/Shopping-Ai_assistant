"""
Recommendation service.

Uses SQLite to select recommended products based on cart items,
then uses AI to rank and enrich recommendations with detailed explanations
via OpenRouter. Falls back to rule-based explanations if the LLM is
unavailable.

Features:
- AI-powered ranking and personalization
- In-memory caching to avoid duplicate LLM calls
- Detailed explanations with confidence scores
- Loading state support
"""
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.review import Review
from app.services.openrouter import (
    explain_recommendation,
    generate_ranked_recommendations,
    RecommendationExplanation,
    RankedRecommendations,
    AIRecommendation,
)


# ── Rule-based mapping ──────────────────────────────────────────────
# Each cart item maps to a list of (product_name_substring, reason) tuples.
# The first tuple defines the primary recommendation; the rest are secondary.
# This is used for BOTH product selection AND fallback explanations.
RECOMMENDATION_RULES: dict[str, list[tuple[str, str]]] = {
    "Milk": [
        ("Greek Yogurt", "Pairs perfectly with milk for a protein-rich breakfast."),
        ("Cheddar Cheese", "Complete your dairy selection with aged cheddar."),
        ("Free Range Eggs", "Milk and eggs are breakfast staples."),
    ],
    "Bread": [
        ("Almond Butter", "Spread almond butter on fresh bread for a healthy snack."),
        ("Cheddar Cheese", "Make a classic grilled cheese sandwich."),
        ("Free Range Eggs", "Bread and eggs make the perfect toast and eggs combo."),
    ],
    "Eggs": [
        ("Organic Whole Milk", "Eggs and milk go hand in hand for baking and breakfast."),
        ("Sourdough Bread", "Enjoy eggs on fresh sourdough toast."),
        ("Cheddar Cheese", "Add cheese to your omelette for extra flavor."),
    ],
    "Yogurt": [
        ("Frozen Mixed Berries", "Top your yogurt with frozen berries for a delicious parfait."),
        ("Organic Bananas", "Slice bananas into yogurt for natural sweetness."),
        ("Granola", None),  # fallback – no exact product match, will use category logic
    ],
    "Tomatoes": [
        ("Schezwan Sauce", "Use tomatoes and Schezwan sauce for a spicy stir-fry."),
        ("Sourdough Bread", "Make bruschetta with fresh tomatoes and bread."),
        ("Basmati Rice", "Tomatoes are essential for a classic tomato rice."),
    ],
    "Bananas": [
        ("Frozen Mixed Berries", "Blend bananas with mixed berries for a tropical smoothie."),
        ("Greek Yogurt", "Bananas and yogurt make a great snack."),
        ("Almond Butter", "Spread almond butter on bananas for a healthy treat."),
    ],
    "Coffee": [
        ("Organic Whole Milk", "Add milk to your coffee for a creamy latte."),
        ("Dark Chocolate Bar 70%", "Pair coffee with dark chocolate for a luxurious treat."),
        ("Almond Butter", None),
    ],
    "Chocolate": [
        ("Instant Coffee Granules", "Dark chocolate and coffee are a classic pairing."),
        ("Organic Whole Milk", "Enjoy chocolate with a glass of cold milk."),
        ("Frozen Mixed Berries", "Dip berries in melted chocolate for a dessert."),
    ],
    "Rice": [
        ("Schezwan Sauce", "Add Schezwan sauce to rice for a spicy kick."),
        ("Free Range Eggs", "Make egg fried rice with leftover rice."),
        ("Roma Tomatoes", "Tomatoes and rice are a staple combination."),
    ],
    "Chips": [
        ("Schezwan Sauce", "Dip chips in Schezwan sauce for a spicy snack."),
        ("Dark Chocolate Bar 70%", "Balance salty chips with dark chocolate."),
        ("Sparkling Water Lime", "Pair chips with sparkling water."),
    ],
    "Cheese": [
        ("Sourdough Bread", "Cheese and bread are a timeless combination."),
        ("Roma Tomatoes", "Tomato and cheese caprese salad."),
        ("Sparkling Water Lime", None),
    ],
    "Butter": [
        ("Sourdough Bread", "Spread butter on warm sourdough bread."),
        ("Organic Bananas", None),
        ("Dark Chocolate Bar 70%", None),
    ],
    "Berries": [
        ("Greek Yogurt", "Mix berries into yogurt for a healthy breakfast."),
        ("Organic Whole Milk", "Blend berries with milk for a smoothie."),
        ("Almond Butter", None),
    ],
}


# ── In-memory cache for AI recommendations ─────────────────────────────
# Cache structure: {cache_key: (timestamp, response_data)}
_RECOMMENDATION_CACHE: Dict[str, Tuple[float, List[dict]]] = {}
_CACHE_TTL_SECONDS = 300  # 5 minutes


def _get_cache_key(cart_items: List[str], product_ids: List[int]) -> str:
    """Generate a cache key from cart items and candidate product IDs."""
    # Sort to ensure consistent cache keys regardless of order
    cart_key = ",".join(sorted(cart_items))
    products_key = ",".join(map(str, sorted(product_ids)))
    combined = f"{cart_key}|{products_key}"
    return hashlib.md5(combined.encode()).hexdigest()


def _get_cached_recommendations(cache_key: str) -> Optional[List[dict]]:
    """Get cached recommendations if still valid."""
    if cache_key not in _RECOMMENDATION_CACHE:
        return None
    
    timestamp, data = _RECOMMENDATION_CACHE[cache_key]
    if time.time() - timestamp > _CACHE_TTL_SECONDS:
        # Cache expired
        del _RECOMMENDATION_CACHE[cache_key]
        return None
    
    return data


def _cache_recommendations(cache_key: str, data: List[dict]) -> None:
    """Cache recommendations with current timestamp."""
    _RECOMMENDATION_CACHE[cache_key] = (time.time(), data)


def clear_recommendation_cache() -> None:
    """Clear all cached recommendations (useful for testing)."""
    global _RECOMMENDATION_CACHE
    _RECOMMENDATION_CACHE = {}


def _get_default_recommendations(db: Session, limit: int = 3) -> List[Product]:
    """Fallback: return top-rated products when no rules match."""
    return (
        db.query(Product)
        .order_by(Product.rating.desc())
        .limit(limit)
        .all()
    )


def _find_product(db: Session, name_substring: str) -> Optional[Product]:
    """Find a product whose name contains the given substring (case-insensitive)."""
    return (
        db.query(Product)
        .filter(Product.name.ilike(f"%{name_substring}%"))
        .first()
    )


def _get_reviews_for_product(db: Session, product_id: int) -> List[str]:
    """Get review texts for a given product."""
    rows = (
        db.query(Review.review)
        .filter(Review.product_id == product_id)
        .all()
    )
    return [row[0] for row in rows]


def _build_product_dict(product: Product, reviews: List[str]) -> Dict[str, Any]:
    """Build a product dict for AI processing."""
    return {
        "name": product.name,
        "price": product.price,
        "rating": product.rating,
        "category": product.category,
        "discount": product.discount,
        "reviews": reviews,
    }


def _build_llm_explanation(
    db: Session,
    cart: List[str],
    product: Product,
) -> Optional[RecommendationExplanation]:
    """Attempt to generate an LLM explanation for a product recommendation."""
    reviews = _get_reviews_for_product(db, product.id)
    if not reviews:
        return None

    return explain_recommendation(
        cart_items=cart,
        product_name=product.name,
        product_price=product.price,
        product_rating=product.rating,
        product_category=product.category,
        reviews=reviews,
        product_discount=product.discount,
    )


def _normalize_product_name(name: str) -> str:
    """Normalize a product name for comparison.
    
    - Trims whitespace
    - Removes duplicate spaces
    - Converts to lowercase
    """
    return " ".join(name.strip().lower().split())


def get_recommendations(cart: List[str], db: Session) -> List[dict]:
    """
    Return up to 3 AI-ranked recommendations based on the items in the cart.

    Flow:
    1. Select candidate products using rule-based mapping
    2. Check cache for existing AI-ranked recommendations
    3. If not cached, call AI to rank and enrich recommendations
    4. Fall back to rule-based explanations if AI fails
    5. Cache the results

    Output keys: product, rating, price, discount, confidence, why, when,
                 best_for, review_summary, pros, cons, recommendation_reason
    """
    # Normalize cart items for filtering
    cart_normalized = {_normalize_product_name(item) for item in cart}
    
    seen_names: set = set()
    cart_lower = [item.lower() for item in cart]

    # Collect all possible rule-based picks in order
    candidate_picks: List[tuple[Product, str]] = []

    for cart_item in cart:
        normalized_key = cart_item.strip()
        for rule_key, rules in RECOMMENDATION_RULES.items():
            if rule_key.lower() in normalized_key.lower():
                for product_substring, reason in rules:
                    product = _find_product(db, product_substring)
                    # Skip if product is the same as any cart item (case-insensitive)
                    if product and _normalize_product_name(product.name) not in cart_normalized:
                        if product.name not in seen_names:
                            candidate_picks.append(
                                (product, reason or f"Recommended with {cart_item}.")
                            )
                            seen_names.add(product.name)

    # If no rule-based picks found, use fallback
    if not candidate_picks:
        fallback_products = _get_default_recommendations(db, limit=3)
        recommendations = []
        for product in fallback_products:
            base_reason = "Top-rated product you might enjoy."
            entry = _build_fallback_recommendation(product, base_reason, cart, db)
            recommendations.append(entry)
        return recommendations

    # De-duplicate, keeping first occurrence (highest priority)
    seen: set = set()
    unique_picks: list = []
    for product, reason in candidate_picks:
        if product.name not in seen:
            unique_picks.append((product, reason))
            seen.add(product.name)

    # Take top 5 candidates for AI ranking (we'll return top 3)
    top_candidates = unique_picks[:5]
    
    # Check cache first
    candidate_ids = [p[0].id for p in top_candidates]
    cache_key = _get_cache_key(cart, candidate_ids)
    cached_result = _get_cached_recommendations(cache_key)
    
    if cached_result is not None:
        # Return cached result (up to 3 items)
        return cached_result[:3]

    # Try AI-powered ranking
    ai_recommendations = _try_ai_ranking(cart, top_candidates, db, cache_key)
    if ai_recommendations:
        return ai_recommendations[:3]

    # Fallback to rule-based with LLM explanations
    recommendations = []
    for product, reason in top_candidates[:3]:
        llm_explanation = _build_llm_explanation(db, cart, product)
        entry = _build_recommendation_entry(product, reason, llm_explanation, cart)
        recommendations.append(entry)

    # Pad with fallback if fewer than 3
    if len(recommendations) < 3:
        recommended_names = [r["product"] for r in recommendations]
        fallback_query = db.query(Product)
        
        if recommended_names:
            fallback_query = fallback_query.filter(~Product.name.in_(recommended_names))
        
        fallback_products = []
        for product in fallback_query.order_by(Product.rating.desc()).all():
            if _normalize_product_name(product.name) not in cart_normalized:
                fallback_products.append(product)
                if len(fallback_products) >= (3 - len(recommendations)):
                    break
        
        for product in fallback_products:
            base_reason = "Top-rated product you might enjoy."
            entry = _build_fallback_recommendation(product, base_reason, cart, db)
            recommendations.append(entry)

    return recommendations


def _try_ai_ranking(
    cart: List[str],
    candidates: List[tuple[Product, str]],
    db: Session,
    cache_key: str,
) -> Optional[List[dict]]:
    """Attempt to use AI to rank and enrich recommendations."""
    # Prepare candidate products with reviews
    candidate_data = []
    for product, _ in candidates:
        reviews = _get_reviews_for_product(db, product.id)
        candidate_data.append(_build_product_dict(product, reviews))
    
    # Call AI for ranking
    ranked_result = generate_ranked_recommendations(
        cart_items=cart,
        candidate_products=candidate_data,
    )
    
    if not ranked_result or not ranked_result.ranked_recommendations:
        return None
    
    # Build recommendation entries from AI results
    recommendations = []
    product_map = {p.name: p for p, _ in candidates}
    
    for ai_rec in ranked_result.ranked_recommendations[:3]:
        product = product_map.get(ai_rec.product_name)
        if not product:
            continue
        
        entry = {
            "product": product.name,
            "rating": product.rating,
            "price": product.price,
            "discount": product.discount,
            "confidence": ai_rec.confidence,
            "priority": ai_rec.priority,
            "why": ai_rec.why,
            "when": ai_rec.when,
            "best_for": ai_rec.best_for,
            "review_summary": ai_rec.review_summary,
            "pros": ai_rec.pros,
            "cons": ai_rec.cons,
            "recommendation_reason": None,
            "recommendation_type": _determine_recommendation_type(cart, product.name),
        }
        recommendations.append(entry)
    
    # Cache the result
    if recommendations:
        _cache_recommendations(cache_key, recommendations)
    
    return recommendations if recommendations else None


def _build_fallback_recommendation(
    product: Product,
    reason: str,
    cart: List[str],
    db: Session,
) -> dict:
    """Build a fallback recommendation with optional LLM explanation."""
    llm_explanation = _build_llm_explanation(db, cart, product)
    return _build_recommendation_entry(product, reason, llm_explanation)


def _determine_recommendation_type(cart_items: List[str], product_name: str) -> str:
    """Determine the type of recommendation based on cart items and product."""
    cart_lower = [item.lower() for item in cart_items]
    product_lower = product_name.lower()
    
    # Check for meal-related combinations
    meal_keywords = ["breakfast", "lunch", "dinner", "meal"]
    for keyword in meal_keywords:
        if any(keyword in item for item in cart_lower) or keyword in product_lower:
            return "meal_companion"
    
    # Check for frequently bought together patterns
    frequently_bought_together = [
        ("milk", "cereal"), ("bread", "butter"), ("pasta", "sauce"),
        ("rice", "curry"), ("eggs", "bread"), ("coffee", "milk")
    ]
    for item1, item2 in frequently_bought_together:
        if any(item in cart_lower for item in [item1, item2]) and any(item in product_lower for item in [item1, item2]):
            return "frequently_bought_together"
    
    # Check for completing an order
    if len(cart_items) > 0:
        return "completes_your_order"
    
    # Default
    return "popular_combination"


def _build_recommendation_entry(
    product: Product,
    reason: str,
    llm_explanation: Optional[RecommendationExplanation],
    cart_items: List[str] = [],
) -> dict:
    """Build a recommendation dict, using LLM explanation if available."""
    entry = {
        "product": product.name,
        "rating": product.rating,
        "price": product.price,
        "discount": product.discount,
        "why_recommended": None,
        "summary": None,
        "pros": None,
        "cons": None,
        "recommendation_reason": reason,
        "recommendation_type": _determine_recommendation_type(cart_items, product.name),
    }

    if llm_explanation:
        entry["why_recommended"] = llm_explanation.why_recommended
        entry["summary"] = llm_explanation.summary
        entry["pros"] = llm_explanation.pros
        entry["cons"] = llm_explanation.cons

    return entry
