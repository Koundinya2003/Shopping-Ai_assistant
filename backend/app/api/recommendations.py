import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.recommendations import get_recommendations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendationRequest(BaseModel):
    cart: List[str] = []


class RecommendationResponse(BaseModel):
    product: str
    rating: float
    price: float
    discount: int
    # AI-powered fields
    confidence: Optional[int] = None
    priority: Optional[str] = None
    why: Optional[str] = None
    when: Optional[str] = None
    best_for: Optional[str] = None
    review_summary: Optional[str] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    recommendation_type: Optional[str] = None
    # Legacy fields (kept for backward compatibility)
    why_recommended: Optional[str] = None
    summary: Optional[str] = None
    recommendation_reason: Optional[str] = None


@router.post("/", response_model=List[RecommendationResponse])
async def create_recommendations(
    body: RecommendationRequest,
    db: Session = Depends(get_db),
):
    """Return 3 contextually relevant product recommendations based on cart items.

    When cart is empty, returns top-rated products as default recommendations.
    """
    try:
        return get_recommendations(body.cart, db)
    except Exception as e:
        logger.error("Failed to generate recommendations: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate recommendations. Please try again later.",
        )
