"""
Unit tests for AI-powered recommendation features.

Tests cover:
- AI ranking integration
- Caching mechanism
- Fallback behavior
- Response schema validation
"""
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
import pytest
import time

from app.models.product import Product
from app.models.review import Review
from app.services.recommendations import (
    get_recommendations,
    _get_cache_key,
    _get_cached_recommendations,
    _cache_recommendations,
    clear_recommendation_cache,
    _try_ai_ranking,
    _RECOMMENDATION_CACHE,
)
from app.services.openrouter import (
    generate_ranked_recommendations,
    RankedRecommendations,
    AIRecommendation,
)


class TestCaching:
    """Test in-memory caching functionality."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_recommendation_cache()

    def test_cache_key_generation(self):
        """Should generate consistent cache keys."""
        cart1 = ["Milk", "Bread"]
        cart2 = ["Bread", "Milk"]  # Different order
        product_ids1 = [1, 2, 3]
        product_ids2 = [3, 2, 1]  # Different order

        key1 = _get_cache_key(cart1, product_ids1)
        key2 = _get_cache_key(cart2, product_ids2)

        # Should generate same key regardless of order
        assert key1 == key2

    def test_cache_miss_for_new_key(self):
        """Should return None for non-existent cache key."""
        result = _get_cached_recommendations("nonexistent_key")
        assert result is None

    def test_cache_hit_and_storage(self):
        """Should store and retrieve cached recommendations."""
        test_data = [{"product": "Test Product", "confidence": 90}]
        cache_key = "test_key"

        _cache_recommendations(cache_key, test_data)
        result = _get_cached_recommendations(cache_key)

        assert result is not None
        assert result == test_data

    def test_cache_expiration(self):
        """Should expire cached recommendations after TTL."""
        test_data = [{"product": "Test Product"}]
        cache_key = "test_key"

        _cache_recommendations(cache_key, test_data)

        # Manually set timestamp to expired
        from app.services.recommendations import _RECOMMENDATION_CACHE
        _RECOMMENDATION_CACHE[cache_key] = (time.time() - 301, test_data)

        result = _get_cached_recommendations(cache_key)
        assert result is None

    def test_clear_cache(self):
        """Should clear all cached recommendations."""
        _cache_recommendations("key1", [{"product": "Product 1"}])
        _cache_recommendations("key2", [{"product": "Product 2"}])

        clear_recommendation_cache()

        # Import fresh to get cleared cache
        from app.services.recommendations import _RECOMMENDATION_CACHE as fresh_cache
        assert len(fresh_cache) == 0


class TestAIRanking:
    """Test AI-powered ranking functionality."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_recommendation_cache()

    @patch("app.services.recommendations.generate_ranked_recommendations")
    def test_ai_ranking_success(self, mock_generate_ranked):
        """Should use AI ranking when available."""
        # Mock AI response
        mock_generate_ranked.return_value = RankedRecommendations(
            shopping_goal="Complete your healthy breakfast with protein-rich dairy",
            ai_tip="Greek yogurt pairs perfectly with milk for a nutritious morning meal",
            ranked_recommendations=[
                AIRecommendation(
                    product_name="Greek Yogurt Plain",
                    confidence=92,
                    priority="high",
                    why="Customers buying milk frequently add Greek yogurt for a protein-rich breakfast. Reviews highlight the creamy texture and health benefits.",
                    when="For weekday breakfasts",
                    best_for="Health-conscious families",
                    review_summary="Customers praise the thick consistency and probiotic benefits. Some mention it's slightly tangy.",
                    pros=["High in protein", "Creamy texture", "Good value for money"],
                    cons=["Slightly tangy taste", "Shorter shelf life"],
                )
            ]
        )

        # Setup products
        milk = Product(
            id=1, name="Organic Whole Milk", category="Dairy",
            price=3.49, rating=4.5, discount=0, image_url="/products/milk.png", unit="1 L"
        )
        yogurt = Product(
            id=2, name="Greek Yogurt Plain", category="Dairy",
            price=5.49, rating=4.1, discount=0, image_url="/products/greek-yogurt.png", unit="400 g tub"
        )

        db = MagicMock(spec=Session)

        def find_product(db_arg, substring):
            if "yogurt" in substring.lower():
                return yogurt
            return None

        # Mock reviews
        db.query.return_value.filter.return_value.all.return_value = [
            ("Great yogurt!",), ("Love the texture",)
        ]

        with patch("app.services.recommendations._find_product", side_effect=find_product):
            cart = ["Milk"]
            recommendations = get_recommendations(cart, db)

            # Verify AI-powered fields are present
            assert len(recommendations) > 0
            rec = recommendations[0]
            assert rec.get("confidence") == 92
            assert rec.get("why") is not None
            assert rec.get("when") == "For weekday breakfasts"
            assert rec.get("best_for") == "Health-conscious families"
            assert rec.get("review_summary") is not None
            assert len(rec.get("pros", [])) == 3
            assert len(rec.get("cons", [])) == 2

    @patch("app.services.recommendations.generate_ranked_recommendations")
    def test_ai_ranking_fallback_on_failure(self, mock_generate_ranked):
        """Should fall back to rule-based when AI fails."""
        mock_generate_ranked.return_value = None

        yogurt = Product(
            id=2, name="Greek Yogurt Plain", category="Dairy",
            price=5.49, rating=4.1, discount=0, image_url="/products/greek-yogurt.png", unit="400 g tub"
        )

        db = MagicMock(spec=Session)

        def find_product(db_arg, substring):
            if "yogurt" in substring.lower():
                return yogurt
            return None

        with patch("app.services.recommendations._find_product", side_effect=find_product):
            with patch("app.services.recommendations._build_llm_explanation", return_value=None):
                cart = ["Milk"]
                recommendations = get_recommendations(cart, db)

                # Should still return recommendations via fallback
                assert len(recommendations) > 0

    @patch("app.services.recommendations.generate_ranked_recommendations")
    def test_caching_prevents_duplicate_ai_calls(self, mock_generate_ranked):
        """Should not call AI again for same cart and products."""
        mock_generate_ranked.return_value = RankedRecommendations(
            shopping_goal="Test shopping goal",
            ai_tip="Test AI tip",
            ranked_recommendations=[
                AIRecommendation(
                    product_name="Greek Yogurt Plain",
                    confidence=90,
                    priority="medium",
                    why="Test explanation",
                    when="Test when",
                    best_for="Test best for",
                    review_summary="Test summary",
                    pros=["Pro 1"],
                    cons=["Con 1"],
                )
            ]
        )

        yogurt = Product(
            id=2, name="Greek Yogurt Plain", category="Dairy",
            price=5.49, rating=4.1, discount=0, image_url="/products/greek-yogurt.png", unit="400 g tub"
        )

        db = MagicMock(spec=Session)

        def find_product(db_arg, substring):
            if "yogurt" in substring.lower():
                return yogurt
            return None

        db.query.return_value.filter.return_value.all.return_value = [
            ("Great yogurt!",), ("Love it",)
        ]

        with patch("app.services.recommendations._find_product", side_effect=find_product):
            cart = ["Milk"]

            # First call
            recommendations1 = get_recommendations(cart, db)
            assert mock_generate_ranked.call_count == 1

            # Second call with same cart
            recommendations2 = get_recommendations(cart, db)
            # Should use cache, not call AI again
            assert mock_generate_ranked.call_count == 1

            # Results should be identical
            assert recommendations1 == recommendations2


class TestResponseSchema:
    """Test that response schema matches requirements."""

    @patch("app.services.recommendations.generate_ranked_recommendations")
    def test_ai_response_schema(self, mock_generate_ranked):
        """Should return all required AI fields."""
        # Clear cache to ensure fresh AI call
        clear_recommendation_cache()
        
        mock_generate_ranked.return_value = RankedRecommendations(
            shopping_goal="Build a nutritious breakfast with complementary items",
            ai_tip="Add Greek yogurt to your cart for a protein boost with your milk",
            ranked_recommendations=[
                AIRecommendation(
                    product_name="Greek Yogurt Plain",
                    confidence=92,
                    priority="high",
                    why="Customers buying milk frequently add Greek yogurt for a protein-rich breakfast. Reviews highlight the creamy texture and probiotic benefits that complement milk perfectly.",
                    when="For weekday breakfasts",
                    best_for="Health-conscious families",
                    review_summary="Customers love the creamy texture and health benefits. Many mention it's perfect for breakfast bowls.",
                    pros=["High in protein", "Creamy texture", "Good value for money"],
                    cons=["Slightly tangy taste", "Shorter shelf life than expected"],
                )
            ]
        )

        yogurt = Product(
            id=2, name="Greek Yogurt Plain", category="Dairy",
            price=5.49, rating=4.1, discount=0, image_url="/products/greek-yogurt.png", unit="400 g tub"
        )

        db = MagicMock(spec=Session)

        def find_product(db_arg, substring):
            if "yogurt" in substring.lower():
                return yogurt
            return None

        db.query.return_value.filter.return_value.all.return_value = [
            ("Great yogurt!",), ("Love it",)
        ]

        with patch("app.services.recommendations._find_product", side_effect=find_product):
            cart = ["Milk"]
            recommendations = get_recommendations(cart, db)

            assert len(recommendations) > 0
            rec = recommendations[0]

            # Verify all required fields
            assert "product" in rec
            assert "rating" in rec
            assert "price" in rec
            assert "discount" in rec
            assert "confidence" in rec
            assert "why" in rec
            assert "when" in rec
            assert "best_for" in rec
            assert "review_summary" in rec
            assert "pros" in rec
            assert "cons" in rec

            # Verify data types and values
            assert isinstance(rec["confidence"], int)
            assert rec["confidence"] == 92  # Should match AI response
            assert 0 <= rec["confidence"] <= 100
            assert isinstance(rec["why"], str)
            assert len(rec["why"]) > 20  # Should be detailed from AI
            assert "milk" in rec["why"].lower()  # Should reference cart item
            assert "yogurt" in rec["why"].lower()  # Should reference recommended product
            assert isinstance(rec["pros"], list)
            assert 2 <= len(rec["pros"]) <= 3
            assert isinstance(rec["cons"], list)
            assert 1 <= len(rec["cons"]) <= 2

    def test_fallback_schema(self):
        """Should return valid schema even in fallback mode."""
        db = MagicMock(spec=Session)
        db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []

        cart = ["Unknown Product"]
        recommendations = get_recommendations(cart, db)

        # Should return empty list or valid recommendations
        for rec in recommendations:
            assert "product" in rec
            assert "rating" in rec
            assert "price" in rec
            assert "discount" in rec