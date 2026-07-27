import logging
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.product import Product
from app.models.review import Review

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
async def get_products(db: Session = Depends(get_db)) -> List[dict[str, Any]]:
    """Return all products as JSON."""
    try:
        products = db.query(Product).all()
        # Get review counts for all products
        review_counts = dict(
            db.query(Review.product_id, func.count(Review.id))
            .group_by(Review.product_id)
            .all()
        )
        return [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "rating": p.rating,
                "discount": p.discount,
                "image_url": p.image_url,
                "unit": p.unit,
                "reviews_count": review_counts.get(p.id, 0),
            }
            for p in products
        ]
    except Exception as e:
        logger.error("Failed to fetch products: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch products")
