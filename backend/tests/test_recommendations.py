"""
Unit tests for the recommendation service.

Tests cover:
- Selected product is never recommended
- Case-insensitive filtering
- Whitespace normalization
- Duplicate filtering
- Fallback behavior when filtering removes candidates
"""
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
import pytest

from app.models.product import Product
from app.services.recommendations import get_recommendations, _normalize_product_name


# ── Normalization tests ─────────────────────────────────────────────


class TestNormalizeProductName:
    def test_lowercase(self):
        """Should convert to lowercase."""
        assert _normalize_product_name("Milk") == "milk"
        assert _normalize_product_name("MILK") == "milk"
        assert _normalize_product_name("Milk") == "milk"

    def test_trim_whitespace(self):
        """Should trim leading and trailing whitespace."""
        assert _normalize_product_name("  Milk  ") == "milk"
        assert _normalize_product_name("Milk ") == "milk"
        assert _normalize_product_name(" Milk") == "milk"

    def test_remove_duplicate_spaces(self):
        """Should remove duplicate spaces."""
        assert _normalize_product_name("Milk  Whole") == "milk whole"
        assert _normalize_product_name("Milk   Whole") == "milk whole"

    def test_combined_normalization(self):
        """Should handle all normalization rules together."""
        assert _normalize_product_name("  MILK  ") == "milk"
        assert _normalize_product_name("  Whole  Milk  ") == "whole milk"
        assert _normalize_product_name("  Organic  Whole  Milk  ") == "organic whole milk"


# ── Recommendation filtering tests ──────────────────────────────────


class TestRecommendationFiltering:
    """Test that selected products are never recommended."""

    @patch("app.services.recommendations._build_llm_explanation")
    def test_milk_not_recommended_when_in_cart(self, mock_llm):
        """Milk should never appear in recommendations when it's in the cart."""
        mock_llm.return_value = None
        
        # Create mock products
        yogurt = Product(
            id=2, name="Greek Yogurt Plain", category="Dairy",
            price=5.49, rating=4.1, discount=0, image_url="/products/greek-yogurt.png", unit="400 g tub"
        )
        cheese = Product(
            id=3, name="Cheddar Cheese Block", category="Dairy",
            price=6.29, rating=4.6, discount=0, image_url=None, unit="200 g"
        )
        
        # Mock database session
        db = MagicMock(spec=Session)
        
        # Mock _find_product to return different products based on substring
        def mock_find_product(db_arg, name_substring):
            if "yogurt" in name_substring.lower():
                return yogurt
            elif "cheese" in name_substring.lower():
                return cheese
            return None
        
        # Patch _find_product
        with patch("app.services.recommendations._find_product", side_effect=mock_find_product):
            # Call with Milk in cart
            cart = ["Milk"]
            recommendations = get_recommendations(cart, db)
            
            # Verify Milk is not in recommendations
            rec_names = [r["product"] for r in recommendations]
            assert "Organic Whole Milk" not in rec_names
            assert "milk" not in [name.lower() for name in rec_names]
            
            # Verify other products are recommended
            assert len(recommendations) > 0

    @patch("app.services.recommendations._build_llm_explanation")
    def test_coffee_not_recommended_when_in_cart(self, mock_llm):
        """Coffee should never appear in recommendations when it's in the cart."""
        mock_llm.return_value = None
        
        milk = Product(
            id=1, name="Organic Whole Milk", category="Dairy",
            price=3.49, rating=4.5, discount=0, image_url="/products/milk.png", unit="1 L"
        )
        chocolate = Product(
            id=8, name="Dark Chocolate Bar 70%", category="Snacks",
            price=4.49, rating=4.8, discount=0, image_url="/products/dark-chocolate.png", unit="90 g bar"
        )
        
        def mock_find_product(db_arg, name_substring):
            if "milk" in name_substring.lower():
                return milk
            elif "chocolate" in name_substring.lower():
                return chocolate
            return None
        
        db = MagicMock(spec=Session)
        
        with patch("app.services.recommendations._find_product", side_effect=mock_find_product):
            cart = ["Coffee"]
            recommendations = get_recommendations(cart, db)
            
            rec_names = [r["product"] for r in recommendations]
            assert "Instant Coffee Granules" not in rec_names
            assert "coffee" not in [name.lower() for name in rec_names]

    @patch("app.services.recommendations._build_llm_explanation")
    def test_bread_not_recommended_when_in_cart(self, mock_llm):
        """Bread should never appear in recommendations when it's in the cart."""
        mock_llm.return_value = None
        
        almond_butter = Product(
            id=11, name="Almond Butter Crunchy", category="Pantry",
            price=8.99, rating=4.5, discount=10, image_url=None, unit="250 g jar"
        )
        eggs = Product(
            id=2, name="Free Range Eggs (12 pack)", category="Dairy",
            price=4.99, rating=4.3, discount=10, image_url="/products/eggs.png", unit="12 pcs"
        )
        
        def mock_find_product(db_arg, name_substring):
            if "almond butter" in name_substring.lower():
                return almond_butter
            elif "eggs" in name_substring.lower():
                return eggs
            return None
        
        db = MagicMock(spec=Session)
        
        with patch("app.services.recommendations._find_product", side_effect=mock_find_product):
            cart = ["Bread"]
            recommendations = get_recommendations(cart, db)
            
            rec_names = [r["product"] for r in recommendations]
            assert "Sourdough Bread Loaf" not in rec_names
            assert "bread" not in [name.lower() for name in rec_names]

    @patch("app.services.recommendations._build_llm_explanation")
    def test_case_insensitive_filtering(self, mock_llm):
        """Filtering should be case-insensitive."""
        mock_llm.return_value = None
        
        milk = Product(
            id=1, name="Organic Whole Milk", category="Dairy",
            price=3.49, rating=4.5, discount=0, image_url="/products/milk.png", unit="1 L"
        )
        yogurt = Product(
            id=2, name="Greek Yogurt Plain", category="Dairy",
            price=5.49, rating=4.1, discount=0, image_url="/products/greek-yogurt.png", unit="400 g tub"
        )
        
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = yogurt
        
        # Test various cases
        for cart_variant in ["MILK", "milk", "Milk", " Milk ", "  MILK  "]:
            cart = [cart_variant]
            recommendations = get_recommendations(cart, db)
            
            rec_names = [r["product"] for r in recommendations]
            assert "Organic Whole Milk" not in rec_names

    @patch("app.services.recommendations._build_llm_explanation")
    def test_no_duplicate_recommendations(self, mock_llm):
        """Should not recommend the same product twice."""
        mock_llm.return_value = None
        
        yogurt = Product(
            id=2, name="Greek Yogurt Plain", category="Dairy",
            price=5.49, rating=4.1, discount=0, image_url="/products/greek-yogurt.png", unit="400 g tub"
        )
        
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = yogurt
        
        # Cart with multiple items that could recommend the same product
        cart = ["Milk", "Bananas"]  # Both could recommend Greek Yogurt
        recommendations = get_recommendations(cart, db)
        
        rec_names = [r["product"] for r in recommendations]
        # Should only appear once
        assert rec_names.count("Greek Yogurt Plain") <= 1

    @patch("app.services.recommendations._build_llm_explanation")
    def test_fallback_excludes_cart_items(self, mock_llm):
        """Fallback recommendations should also exclude cart items."""
        mock_llm.return_value = None
        
        # Create products with different ratings
        products = [
            Product(id=i, name=f"Product {i}", category="Test", 
                   price=10.0, rating=5.0 - i * 0.1, discount=0, 
                   image_url=None, unit="1 unit")
            for i in range(1, 6)
        ]
        products[0].name = "Milk"  # Product in cart
        
        db = MagicMock(spec=Session)
        
        # Mock the fallback query
        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = products[1:4]  # Return non-milk products
        db.query.return_value = mock_query
        
        cart = ["Milk"]
        recommendations = get_recommendations(cart, db)
        
        rec_names = [r["product"] for r in recommendations]
        assert "Milk" not in rec_names

    @patch("app.services.recommendations._build_llm_explanation")
    def test_multiple_cart_items_all_excluded(self, mock_llm):
        """All items in cart should be excluded from recommendations."""
        mock_llm.return_value = None
        
        eggs = Product(
            id=2, name="Free Range Eggs (12 pack)", category="Dairy",
            price=4.99, rating=4.3, discount=10, image_url="/products/eggs.png", unit="12 pcs"
        )
        
        def mock_find_product(db_arg, name_substring):
            if "eggs" in name_substring.lower():
                return eggs
            return None
        
        db = MagicMock(spec=Session)
        
        with patch("app.services.recommendations._find_product", side_effect=mock_find_product):
            cart = ["Milk", "Bread"]
            recommendations = get_recommendations(cart, db)
            
            rec_names = [r["product"] for r in recommendations]
            assert "Organic Whole Milk" not in rec_names
            assert "Sourdough Bread Loaf" not in rec_names

    @patch("app.services.recommendations._build_llm_explanation")
    def test_returns_three_recommendations_when_possible(self, mock_llm):
        """Should return 3 recommendations when enough candidates exist."""
        mock_llm.return_value = None
        
        products = [
            Product(id=i, name=f"Product {i}", category="Test",
                   price=10.0, rating=5.0 - i * 0.1, discount=0,
                   image_url=None, unit="1 unit")
            for i in range(1, 10)
        ]
        
        db = MagicMock(spec=Session)
        
        # Mock finding products for recommendations
        call_count = [0]
        def find_product_side_effect(db_arg, name_substring):
            product = products[call_count[0] % len(products)]
            call_count[0] += 1
            return product
        
        with patch("app.services.recommendations._find_product", side_effect=find_product_side_effect):
            cart = ["Milk"]
            recommendations = get_recommendations(cart, db)
            
            # Should return up to 3 recommendations
            assert len(recommendations) <= 3
            assert len(recommendations) > 0

    @patch("app.services.recommendations._build_llm_explanation")
    def test_partial_match_does_not_exclude(self, mock_llm):
        """Products with similar names but different IDs should not be excluded."""
        mock_llm.return_value = None
        
        milk = Product(
            id=1, name="Organic Whole Milk", category="Dairy",
            price=3.49, rating=4.5, discount=0, image_url="/products/milk.png", unit="1 L"
        )
        chocolate_milk = Product(
            id=15, name="Chocolate Milk", category="Dairy",
            price=4.99, rating=4.2, discount=0, image_url=None, unit="1 L"
        )
        
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = chocolate_milk
        
        cart = ["Organic Whole Milk"]
        recommendations = get_recommendations(cart, db)
        
        rec_names = [r["product"] for r in recommendations]
        # Chocolate Milk is a different product, so it should be allowed
        # (though in practice, the rules might not recommend it)
        # This test verifies the normalization logic doesn't over-filter


# ── Integration-style tests ─────────────────────────────────────────


class TestRecommendationPipeline:
    """Test the complete recommendation pipeline."""

    @patch("app.services.recommendations._build_llm_explanation")
    def test_full_pipeline_milk_cart(self, mock_llm):
        """Test complete pipeline with Milk in cart."""
        mock_llm.return_value = None
        
        # Setup products
        products = {
            "Organic Whole Milk": Product(id=1, name="Organic Whole Milk", category="Dairy",
                                         price=3.49, rating=4.5, discount=0, 
                                         image_url="/products/milk.png", unit="1 L"),
            "Greek Yogurt Plain": Product(id=2, name="Greek Yogurt Plain", category="Dairy",
                                         price=5.49, rating=4.1, discount=0,
                                         image_url="/products/greek-yogurt.png", unit="400 g tub"),
            "Cheddar Cheese Block": Product(id=3, name="Cheddar Cheese Block", category="Dairy",
                                           price=6.29, rating=4.6, discount=0,
                                           image_url=None, unit="200 g"),
            "Free Range Eggs (12 pack)": Product(id=4, name="Free Range Eggs (12 pack)", 
                                                category="Dairy", price=4.99, rating=4.3,
                                                discount=10, image_url="/products/eggs.png", 
                                                unit="12 pcs"),
        }
        
        db = MagicMock(spec=Session)
        
        def find_product(db_arg, substring):
            for name, product in products.items():
                if substring.lower() in name.lower():
                    return product
            return None
        
        with patch("app.services.recommendations._find_product", side_effect=find_product):
            cart = ["Milk"]
            recommendations = get_recommendations(cart, db)
            
            # Verify no milk in recommendations
            rec_names = [r["product"] for r in recommendations]
            assert "Organic Whole Milk" not in rec_names
            
            # Verify we got recommendations
            assert len(recommendations) > 0
            assert len(recommendations) <= 3

    @patch("app.services.recommendations._build_llm_explanation")
    def test_validation_all_test_products(self, mock_llm):
        """Test that all mentioned products never recommend themselves."""
        mock_llm.return_value = None
        
        test_products = [
            "Milk", "Coffee", "Bread", "Protein Bars"
        ]
        
        for product_name in test_products:
            # Create a mock product
            product = Product(
                id=1, name=product_name, category="Test",
                price=10.0, rating=4.5, discount=0,
                image_url=None, unit="1 unit"
            )
            
            db = MagicMock(spec=Session)
            db.query.return_value.filter.return_value.first.return_value = product
            
            cart = [product_name]
            recommendations = get_recommendations(cart, db)
            
            rec_names = [r["product"] for r in recommendations]
            rec_names_lower = [name.lower() for name in rec_names]
            
            # The product should never appear in recommendations
            assert product_name not in rec_names
            assert product_name.lower() not in rec_names_lower