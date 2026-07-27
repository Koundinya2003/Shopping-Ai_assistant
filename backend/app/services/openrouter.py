"""
OpenRouter service layer.

Handles communication with the OpenRouter API to generate LLM-powered
explanations and summaries. Uses the OpenRouter API endpoint.

Configuration is read from environment variables with sensible defaults.
Prompts are loaded from external text files to avoid hardcoding.
"""
import json
import os
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from pydantic import BaseModel, ValidationError

import httpx

logger = logging.getLogger(__name__)


# ── Structured output models ──────────────────────────────────────────


class RecommendationExplanation(BaseModel):
    """Structured output from the LLM explaining a recommendation."""
    why_recommended: str
    summary: str
    pros: List[str]
    cons: List[str]


class AIRecommendation(BaseModel):
    """Structured output for AI-ranked recommendation."""
    product_name: str
    confidence: int
    priority: str
    why: str
    when: str
    best_for: str
    review_summary: str
    pros: List[str]
    cons: List[str]


class RankedRecommendations(BaseModel):
    """Top-level response for ranked recommendations."""
    shopping_goal: str
    ai_tip: str
    ranked_recommendations: List[AIRecommendation]


class ReviewSummary(BaseModel):
    """Structured output from the LLM for a review summary."""
    summary: str = ""
    pros: List[str] = []
    cons: List[str] = []
    trust_reason: str = ""


# ── Centralized configuration ─────────────────────────────────────────


@dataclass
class OpenRouterConfig:
    """Configuration for the OpenRouter service, read from environment variables."""
    api_key: str = ""
    base_url: str = "https://openrouter.ai/api/v1"
    model: str = "deepseek/deepseek-chat-v3"
    request_timeout: float = 30.0
    max_retries: int = 3
    initial_retry_delay: float = 1.0
    max_retry_delay: float = 10.0
    backoff_multiplier: float = 2.0

    @classmethod
    def from_env(cls) -> "OpenRouterConfig":
        """Build configuration from environment variables."""
        return cls(
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            base_url=os.getenv(
                "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
            ),
            model=os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3"),
            request_timeout=float(
                os.getenv("OPENROUTER_TIMEOUT", "30.0")
            ),
            max_retries=int(
                os.getenv("OPENROUTER_MAX_RETRIES", "3")
            ),
            initial_retry_delay=float(
                os.getenv("OPENROUTER_INITIAL_RETRY_DELAY", "1.0")
            ),
            max_retry_delay=float(
                os.getenv("OPENROUTER_MAX_RETRY_DELAY", "10.0")
            ),
            backoff_multiplier=float(
                os.getenv("OPENROUTER_BACKOFF_MULTIPLIER", "2.0")
            ),
        )


# ── Prompt loading ────────────────────────────────────────────────────


_PROMPT_CACHE: Dict[str, str] = {}


def _load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory.

    Prompts are cached after first load to avoid repeated disk I/O.
    Raises FileNotFoundError if the prompt file does not exist.
    """
    if filename in _PROMPT_CACHE:
        return _PROMPT_CACHE[filename]

    prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
    filepath = prompts_dir / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {filepath}"
        )

    content = filepath.read_text(encoding="utf-8")
    _PROMPT_CACHE[filename] = content
    return content


def _format_prompt(template: str, **kwargs: str) -> str:
    """Substitute placeholders in a prompt template.

    Uses Python's str.format() for placeholder substitution.
    """
    return template.format(**kwargs)


# ── HTTP client helpers ───────────────────────────────────────────────


def _build_client(config: OpenRouterConfig) -> httpx.Client:
    """Build an httpx client with the configured timeout."""
    return httpx.Client(timeout=config.request_timeout)


def _call_llm(
    config: OpenRouterConfig,
    system_prompt: str,
    user_prompt: str,
) -> Optional[str]:
    """Call the OpenRouter API with retry logic and exponential backoff.

    Returns the response content string on success, or None if all retries fail.
    Logs warnings on failure without exposing secrets (API key, etc.).
    """
    if not config.api_key:
        logger.warning("OpenRouter API key is not configured; skipping LLM call.")
        return None

    url = f"{config.base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://blinkit-ai-assistant.local",
        "X-Title": "AI Grocery Assistant",
    }
    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
        "max_tokens": 500,
    }

    last_exception: Optional[Exception] = None
    delay = config.initial_retry_delay

    for attempt in range(1, config.max_retries + 1):
        try:
            with _build_client(config) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return content
        except httpx.TimeoutException as e:
            logger.warning(
                "OpenRouter request timed out (attempt %d/%d)",
                attempt,
                config.max_retries,
            )
            last_exception = e
        except httpx.HTTPStatusError as e:
            logger.warning(
                "OpenRouter returned status %d (attempt %d/%d)",
                e.response.status_code,
                attempt,
                config.max_retries,
            )
            last_exception = e
        except (httpx.RequestError, KeyError, json.JSONDecodeError) as e:
            logger.warning(
                "OpenRouter request failed (attempt %d/%d): %s",
                attempt,
                config.max_retries,
                e,
            )
            last_exception = e

        if attempt < config.max_retries:
            time.sleep(delay)
            delay = min(delay * config.backoff_multiplier, config.max_retry_delay)

    logger.error(
        "OpenRouter request failed after %d attempts",
        config.max_retries,
    )
    return None


# ── Response validation and repair ────────────────────────────────────


def _try_parse_and_validate(
    content: str, model_class: type
) -> Tuple[Optional[BaseModel], Optional[str]]:
    """Attempt to parse and validate LLM response content.

    Returns (parsed_model, None) on success, or (None, error_message) on failure.
    Attempts to repair common JSON issues before giving up.
    """
    # First attempt: direct parsing
    try:
        parsed = json.loads(content)
        return model_class(**parsed), None
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        error = str(e)

    # Repair attempt 1: strip markdown code fences
    cleaned = content.strip()
    if cleaned.startswith("```"):
        # Remove opening fence (possibly with language specifier)
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        # Remove closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        parsed = json.loads(cleaned)
        return model_class(**parsed), None
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        error = str(e)

    # Repair attempt 2: try to extract JSON object from the string
    try:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            extracted = cleaned[start : end + 1]
            parsed = json.loads(extracted)
            return model_class(**parsed), None
    except (json.JSONDecodeError, ValidationError, TypeError):
        pass

    return None, error


# ── Service functions ────────────────────────────────────────────────


_CONFIG: Optional[OpenRouterConfig] = None


def _get_config() -> OpenRouterConfig:
    """Get or create the global configuration singleton."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = OpenRouterConfig.from_env()
    return _CONFIG


def get_config() -> OpenRouterConfig:
    """Public accessor for the configuration (useful in testing)."""
    return _get_config()


def reset_config() -> None:
    """Reset the configuration singleton (useful in testing)."""
    global _CONFIG
    _CONFIG = None


# ── Existing function (kept for backward compatibility) ────────────────

SYSTEM_PROMPT = """You are a helpful grocery shopping assistant. Your task is to explain why a certain product is being recommended to a customer based on what's in their cart.

You will be given:
- The items currently in the customer's cart
- A recommended product (name, price, rating, category, discount)
- A few customer reviews for that product

You must return a JSON object with exactly these fields:
- "why_recommended": A 1-2 sentence explanation of why this product pairs well with the cart items.
- "summary": A 1-2 sentence summary of what customers are saying about this product.
- "pros": An array of 2-3 specific positive points mentioned in the reviews (each 5-10 words).
- "cons": An array of 1-2 specific negative or neutral points mentioned in the reviews (each 5-10 words). If there are no negative points, return an empty array.

Return ONLY valid JSON, no markdown, no code fences."""


def _build_user_prompt(
    cart_items: List[str],
    product_name: str,
    product_price: float,
    product_rating: float,
    product_category: str,
    reviews: List[str],
    product_discount: int = 0,
) -> str:
    """Build the user prompt for the LLM."""
    reviews_text = "\n".join(f"- {r}" for r in reviews)
    return f"""Cart items: {', '.join(cart_items)}

Recommended product:
- Name: {product_name}
- Price: ${product_price:.2f}
- Rating: {product_rating}/5
- Category: {product_category}
- Discount: {product_discount}% off

Customer reviews:
{reviews_text}

Explain why this product is a good recommendation for this customer."""


def explain_recommendation(
    cart_items: List[str],
    product_name: str,
    product_price: float,
    product_rating: float,
    product_category: str,
    reviews: List[str],
    product_discount: int = 0,
) -> Optional[RecommendationExplanation]:
    """
    Call OpenRouter to generate an explanation for a product recommendation.

    Returns a RecommendationExplanation on success, or None if the LLM
    call fails (so callers can fall back to rule-based explanations).
    """
    config = _get_config()
    if not config.api_key:
        return None

    content = _call_llm(
        config=config,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=_build_user_prompt(
            cart_items=cart_items,
            product_name=product_name,
            product_price=product_price,
            product_rating=product_rating,
            product_category=product_category,
            reviews=reviews,
            product_discount=product_discount,
        ),
    )

    if content is None:
        return None

    parsed, error = _try_parse_and_validate(content, RecommendationExplanation)
    if parsed is not None:
        return parsed  # type: ignore[return-value]

    logger.warning("Failed to parse LLM response: %s", error)
    return None


def generate_ranked_recommendations(
    cart_items: List[str],
    candidate_products: List[Dict[str, Any]],
) -> Optional[RankedRecommendations]:
    """
    Call OpenRouter to rank and enrich product recommendations.

    Args:
        cart_items: List of product names in the cart
        candidate_products: List of dicts with product info and reviews
            Each dict should have: name, price, rating, category, discount, reviews

    Returns:
        RankedRecommendations on success, None on failure
    """
    config = _get_config()
    if not config.api_key:
        return None

    try:
        prompt_template = _load_prompt("ai_recommendation.txt")
    except FileNotFoundError:
        logger.error("AI recommendation prompt template not found")
        return None

    # Format candidate products for the prompt
    products_text = "\n".join(
        f"- {p['name']} (Price: ${p['price']:.2f}, Rating: {p['rating']}/5, "
        f"Category: {p['category']}, Discount: {p.get('discount', 0)}% off)\n"
        f"  Reviews: {'; '.join(p.get('reviews', [])[:3])}"
        for p in candidate_products
    )

    user_prompt = _format_prompt(
        prompt_template,
        cart_items=", ".join(cart_items),
        candidate_products=products_text,
    )

    content = _call_llm(
        config=config,
        system_prompt="You are an AI-powered Quick Commerce shopping assistant for Blinkit. Always return valid JSON.",
        user_prompt=user_prompt,
    )

    if content is None:
        return None

    parsed, error = _try_parse_and_validate(content, RankedRecommendations)
    if parsed is not None:
        return parsed  # type: ignore[return-value]

    logger.warning("Failed to parse ranked recommendations response: %s", error)
    return None


# ── New function: generate_review_summary ─────────────────────────────


def generate_review_summary(
    product_name: str,
    reviews: List[str],
) -> Dict[str, Any]:
    """
    Generate a summary of customer reviews for a product using OpenRouter.

    The result is a validated dict with keys: summary, pros, cons, trust_reason.
    If the LLM call fails or returns malformed JSON, a safe fallback is returned.

    Args:
        product_name: The name of the product.
        reviews: A list of customer review strings.

    Returns:
        A dict with keys: summary (str), pros (list[str]), cons (list[str]),
        trust_reason (str). All values default to empty on failure.
    """
    config = _get_config()

    if not config.api_key or not reviews:
        return {"summary": "", "pros": [], "cons": [], "trust_reason": ""}

    try:
        prompt_template = _load_prompt("review_summary.txt")
    except FileNotFoundError:
        logger.error("Prompt template 'review_summary.txt' not found.")
        return {"summary": "", "pros": [], "cons": [], "trust_reason": ""}

    reviews_text = "\n".join(f"- {r}" for r in reviews)
    user_prompt = _format_prompt(
        prompt_template,
        product_name=product_name,
        reviews_text=reviews_text,
    )

    # System prompt is the same as the instruction prompt for this use case
    content = _call_llm(
        config=config,
        system_prompt="You are a helpful grocery shopping assistant.",
        user_prompt=user_prompt,
    )

    if content is None:
        return {"summary": "", "pros": [], "cons": [], "trust_reason": ""}

    parsed, error = _try_parse_and_validate(content, ReviewSummary)
    if parsed is not None:
        return parsed.model_dump()

    logger.warning(
        "Failed to parse review summary response, returning fallback. Error: %s",
        error,
    )
    return {"summary": "", "pros": [], "cons": [], "trust_reason": ""}