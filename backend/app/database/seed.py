"""
Seed the database with 15 realistic grocery products and 8-10 reviews per product.
"""
import logging
from app.database import SessionLocal, init_db
from app.models.product import Product
from app.models.review import Review

logger = logging.getLogger(__name__)


PRODUCTS = [
    {"name": "Organic Whole Milk", "category": "Dairy", "price": 3.49, "rating": 4.5, "discount": 0, "image_url": "/products/milk.png", "unit": "1 L"},
    {"name": "Free Range Eggs (12 pack)", "category": "Dairy", "price": 4.99, "rating": 4.3, "discount": 10, "image_url": "/products/eggs.png", "unit": "12 pcs"},
    {"name": "Greek Yogurt Plain", "category": "Dairy", "price": 5.49, "rating": 4.1, "discount": 0, "image_url": "/products/greek-yogurt.png", "unit": "400 g tub"},
    {"name": "Sourdough Bread Loaf", "category": "Bakery", "price": 4.29, "rating": 4.7, "discount": 0, "image_url": "/products/bread.png", "unit": "400 g"},
    {"name": "Roma Tomatoes (1 lb)", "category": "Produce", "price": 2.99, "rating": 4.0, "discount": 15, "image_url": "/products/tomatoes.png", "unit": "500 g"},
    {"name": "Organic Bananas (bunch)", "category": "Produce", "price": 1.49, "rating": 4.6, "discount": 0, "image_url": "/products/bananas.png", "unit": "6 pcs"},
    {"name": "Potato Chips Sea Salt", "category": "Snacks", "price": 3.99, "rating": 4.2, "discount": 5, "image_url": "/products/chips.png", "unit": "90 g"},
    {"name": "Dark Chocolate Bar 70%", "category": "Snacks", "price": 4.49, "rating": 4.8, "discount": 0, "image_url": "/products/dark-chocolate.png", "unit": "90 g bar"},
    {"name": "Instant Coffee Granules", "category": "Beverages", "price": 6.99, "rating": 3.9, "discount": 20, "image_url": "/products/instant-coffee.png", "unit": "100 g jar"},
    {"name": "Schezwan Sauce", "category": "Condiments", "price": 3.29, "rating": 4.4, "discount": 0, "image_url": "/products/schezwan-sauce.png", "unit": "250 g jar"},
    {"name": "Almond Butter Crunchy", "category": "Pantry", "price": 8.99, "rating": 4.5, "discount": 10, "image_url": None, "unit": "250 g jar"},
    {"name": "Basmati Rice (2 lb)", "category": "Pantry", "price": 5.99, "rating": 4.3, "discount": 0, "image_url": None, "unit": "2 lb"},
    {"name": "Cheddar Cheese Block", "category": "Dairy", "price": 6.29, "rating": 4.6, "discount": 0, "image_url": None, "unit": "200 g"},
    {"name": "Sparkling Water Lime", "category": "Beverages", "price": 4.99, "rating": 3.8, "discount": 0, "image_url": None, "unit": "1 L"},
    {"name": "Frozen Mixed Berries", "category": "Frozen", "price": 7.49, "rating": 4.2, "discount": 0, "image_url": None, "unit": "400 g bag"},
]

REVIEWS_BY_PRODUCT = {
    "Organic Whole Milk": [
        ("Great quality milk, stays fresh for a long time.", "positive"),
        ("My kids love this milk. Will buy again.", "positive"),
        ("A bit pricey but worth it for organic.", "neutral"),
        ("Creamy and delicious. Perfect for coffee.", "positive"),
        ("Packaging could be better, leaked a little.", "negative"),
        ("Best organic milk in the store.", "positive"),
        ("Good value for the price.", "positive"),
        ("Consistently fresh every time I order.", "positive"),
        ("Not as fresh as local dairy but convenient.", "neutral"),
    ],
    "Free Range Eggs (12 pack)": [
        ("Perfect eggs for baking and omelettes.", "positive"),
        ("The yolks are so orange and rich!", "positive"),
        ("Some eggs were cracked on delivery.", "negative"),
        ("Good quality free range eggs.", "positive"),
        ("I use these every morning for breakfast.", "positive"),
        ("Better than the regular ones, noticeable difference.", "positive"),
        ("A bit expensive for 12 eggs.", "neutral"),
        ("Fresh and farm-like taste.", "positive"),
        ("Consistent size and quality.", "positive"),
        ("Would prefer larger eggs for the price.", "neutral"),
    ],
    "Greek Yogurt Plain": [
        ("Thick and creamy, perfect for smoothies.", "positive"),
        ("High protein content, great for post-workout.", "positive"),
        ("Tastes a bit sour compared to other brands.", "neutral"),
        ("My go-to yogurt for breakfast bowls.", "positive"),
        ("Good consistency but wish it came in larger tubs.", "neutral"),
        ("Excellent for making tzatziki sauce.", "positive"),
        ("Not as thick as I expected.", "negative"),
        ("Clean ingredients, no artificial stuff.", "positive"),
        ("Great value for the protein you get.", "positive"),
    ],
    "Sourdough Bread Loaf": [
        ("Best sourdough I've had from a grocery store.", "positive"),
        ("Perfect crust and chewy inside.", "positive"),
        ("Stays fresh for days, makes great toast.", "positive"),
        ("A bit too tangy for my taste.", "neutral"),
        ("Love the artisanal quality.", "positive"),
        ("Makes amazing grilled cheese sandwiches.", "positive"),
        ("Slices are unevenly cut.", "negative"),
        ("Freshly baked and smells wonderful.", "positive"),
        ("Worth every penny for bread lovers.", "positive"),
        ("Gets stale quickly, eat within 2 days.", "neutral"),
    ],
    "Roma Tomatoes (1 lb)": [
        ("Firm and ripe, perfect for pasta sauce.", "positive"),
        ("Good quality tomatoes for cooking.", "positive"),
        ("Some were a bit mushy on arrival.", "negative"),
        ("Great flavor, better than supermarket standard.", "positive"),
        ("Used for salsa and they were perfect.", "positive"),
        ("Fair price for the quality.", "positive"),
        ("Could be more consistent in ripeness.", "neutral"),
        ("Organic and tasty, will order again.", "positive"),
        ("Not the best I've had but decent.", "neutral"),
    ],
    "Organic Bananas (bunch)": [
        ("Perfectly ripe, not too green not too brown.", "positive"),
        ("Sweet and delicious, great for smoothies.", "positive"),
        ("Arrived with some bruising.", "negative"),
        ("Best bananas in the store, always fresh.", "positive"),
        ("Good size bunch with 6 bananas.", "positive"),
        ("Organic and affordable.", "positive"),
        ("Ripened nicely over a few days.", "positive"),
        ("Could be cheaper but quality is good.", "neutral"),
        ("Consistently good every order.", "positive"),
        ("My toddler loves these bananas.", "positive"),
    ],
    "Potato Chips Sea Salt": [
        ("Crunchy and perfectly salted.", "positive"),
        ("Great snack, the bag was full not half air.", "positive"),
        ("Addictive! Can't stop eating them.", "positive"),
        ("Classic chips done right.", "positive"),
        ("Good for parties and gatherings.", "positive"),
        ("A bit too oily for my liking.", "neutral"),
        ("Fresh and crispy, not stale.", "positive"),
        ("Best price for the size of bag.", "positive"),
        ("Could use a bit more salt.", "neutral"),
        ("My favorite chip brand by far.", "positive"),
    ],
    "Dark Chocolate Bar 70%": [
        ("Rich and smooth, high quality chocolate.", "positive"),
        ("Perfect balance of bitter and sweet.", "positive"),
        ("Melts beautifully for baking.", "positive"),
        ("Best dark chocolate at this price point.", "positive"),
        ("Intense cocoa flavor, exactly what I wanted.", "positive"),
        ("A bit grainy texture.", "negative"),
        ("Great for keto diet, low sugar.", "positive"),
        ("I buy this every week, love it.", "positive"),
        ("Smooth and satisfying after dinner treat.", "positive"),
        ("Wish it came in a bigger bar.", "neutral"),
    ],
    "Instant Coffee Granules": [
        ("Convenient and tastes decent for instant.", "positive"),
        ("Not as good as brewed but quick and easy.", "neutral"),
        ("Great for camping and travel.", "positive"),
        ("Dissolves well in hot water, no clumps.", "positive"),
        ("A bit bitter, needs milk to balance.", "neutral"),
        ("Best instant coffee I've tried.", "positive"),
        ("Good value for the price.", "positive"),
        ("Smooth taste, not acidic.", "positive"),
        ("Works well for iced coffee too.", "positive"),
        ("Could be stronger, I need 2 spoons.", "negative"),
    ],
    "Schezwan Sauce": [
        ("Amazing flavor, spicy and tangy.", "positive"),
        ("Perfect for stir fry and noodles.", "positive"),
        ("Authentic Schezwan taste, love it.", "positive"),
        ("A bit too spicy for my family.", "neutral"),
        ("Great condiment to have in the pantry.", "positive"),
        ("Better than restaurant quality sauce.", "positive"),
        ("Bottle is small for the price.", "negative"),
        ("Adds amazing flavor to any dish.", "positive"),
        ("Good heat level, not overwhelming.", "positive"),
        ("I put this on everything now.", "positive"),
    ],
    "Almond Butter Crunchy": [
        ("Smooth and creamy with nice crunch.", "positive"),
        ("Clean ingredients, just almonds and salt.", "positive"),
        ("A bit expensive but quality is great.", "neutral"),
        ("Perfect spread on toast and apples.", "positive"),
        ("No stirring needed, doesn't separate.", "positive"),
        ("Tastes fresh and natural.", "positive"),
        ("Could be creamier, a bit dry.", "negative"),
        ("Great protein source for snacks.", "positive"),
        ("Love the crunchy texture.", "positive"),
        ("Better than peanut butter alternative.", "positive"),
    ],
    "Basmati Rice (2 lb)": [
        ("Fragrant and fluffy after cooking.", "positive"),
        ("Perfect for biryani and pulao.", "positive"),
        ("Good quality long grain rice.", "positive"),
        ("A bit pricey for 2 lbs.", "neutral"),
        ("Aromatic and cooks evenly.", "positive"),
        ("Best rice for Indian dishes.", "positive"),
        ("Some grains were broken.", "negative"),
        ("Consistent quality every purchase.", "positive"),
        ("Washes clean, not too starchy.", "positive"),
        ("Great value for premium rice.", "positive"),
    ],
    "Frozen Mixed Berries": [
        ("Perfect for smoothies and baking.", "positive"),
        ("Good mix of strawberries, blueberries, raspberries.", "positive"),
        ("Some berries were mushy after thawing.", "negative"),
        ("Convenient and saves time on prep.", "positive"),
        ("Great for overnight oats.", "positive"),
        ("Sweet and flavorful even frozen.", "positive"),
        ("Bag could be bigger for the price.", "neutral"),
        ("No added sugar, just pure fruit.", "positive"),
        ("Perfect for making jam.", "positive"),
        ("Good quality frozen fruit.", "positive"),
    ],
    "Cheddar Cheese Block": [
        ("Sharp and flavorful cheddar.", "positive"),
        ("Melts perfectly for grilled cheese.", "positive"),
        ("Great quality cheese block.", "positive"),
        ("A bit dry compared to other brands.", "negative"),
        ("Perfect for cheese boards.", "positive"),
        ("Strong flavor, a little goes a long way.", "positive"),
        ("Good price for the size.", "positive"),
        ("Fresh and not oily.", "positive"),
        ("Best cheddar for mac and cheese.", "positive"),
        ("Wraps well and stays fresh.", "positive"),
    ],
    "Sparkling Water Lime": [
        ("Refreshing and crisp, no artificial taste.", "positive"),
        ("Great alternative to soda.", "positive"),
        ("Lime flavor is subtle and natural.", "positive"),
        ("Could be more carbonated.", "neutral"),
        ("Perfect for mixing with cocktails.", "positive"),
        ("Best sparkling water brand.", "positive"),
        ("A bit flat compared to competitors.", "negative"),
        ("Good value for a 12-pack.", "positive"),
        ("Refreshing on a hot day.", "positive"),
        ("No weird aftertaste like some brands.", "positive"),
    ],
}


def seed():
    """Seed the database with products and reviews."""
    init_db()
    db = SessionLocal()

    # Check if already seeded
    existing = db.query(Product).count()
    if existing > 0:
        logger.info("Database already has %d products. Skipping seed.", existing)
        db.close()
        return

    # Insert products
    product_objects = {}
    for p in PRODUCTS:
        product = Product(**p)
        db.add(product)
        db.flush()  # Get the id
        product_objects[product.name] = product

    # Insert reviews
    for product_name, reviews in REVIEWS_BY_PRODUCT.items():
        product = product_objects[product_name]
        for review_text, sentiment in reviews:
            review = Review(
                product_id=product.id,
                review=review_text,
                sentiment=sentiment,
            )
            db.add(review)

    db.commit()
    db.close()
    logger.info(
        "Seeded %d products and %d reviews.",
        len(PRODUCTS),
        sum(len(v) for v in REVIEWS_BY_PRODUCT.values()),
    )


if __name__ == "__main__":
    seed()