# API Documentation

## Base URL

Development: `http://localhost:8000`  
Production: Set via `NEXT_PUBLIC_API_URL` environment variable on the frontend.

---

## Endpoints

### 1. Health Check

**Purpose:** Verify the server is running.

- **Method:** `GET`
- **URL:** `/`
- **Request Body:** None
- **Response Schema:**
  ```json
  {
    "status": "string",
    "service": "string"
  }
  ```

**Example Request:**
```bash
curl http://localhost:8000/
```

**Example Response (200 OK):**
```json
{
  "status": "running",
  "service": "AI Grocery Assistant"
}
```

**Possible Errors:** None

---

### 2. List Products

**Purpose:** Retrieve all available products with review counts.

- **Method:** `GET`
- **URL:** `/products/`
- **Request Body:** None
- **Response Schema:** Array of:
  ```json
  {
    "id": "integer",
    "name": "string",
    "category": "string",
    "price": "float",
    "rating": "float",
    "discount": "integer",
    "image_url": "string | null",
    "unit": "string",
    "reviews_count": "integer"
  }
  ```

**Example Request:**
```bash
curl http://localhost:8000/products/
```

**Example Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Organic Whole Milk",
    "category": "Dairy",
    "price": 3.49,
    "rating": 4.5,
    "discount": 0,
    "image_url": "/products/milk.png",
    "unit": "1 L",
    "reviews_count": 9
  },
  {
    "id": 2,
    "name": "Free Range Eggs (12 pack)",
    "category": "Dairy",
    "price": 4.99,
    "rating": 4.3,
    "discount": 10,
    "image_url": "/products/eggs.png",
    "unit": "12 pcs",
    "reviews_count": 10
  }
]
```

**Possible Errors:**
| Status | Description |
|--------|-------------|
| 500 | Failed to fetch products (internal server error) |

---

### 3. Get Recommendations

**Purpose:** Generate up to 3 product recommendations based on cart items. Uses rule-based product matching with optional LLM-powered explanations.

- **Method:** `POST`
- **URL:** `/recommendations/`
- **Request Body:**
  ```json
  {
    "cart": ["string", "..."]
  }
  ```
  - `cart`: Array of product names currently in the user's cart (can be empty).

- **Response Schema:** Array of:
  ```json
  {
    "product": "string",
    "rating": "float",
    "price": "float",
    "discount": "integer",
    "why_recommended": "string | null",
    "summary": "string | null",
    "pros": ["string", "..."] | null,
    "cons": ["string", "..."] | null
  }
  ```

**Example Request:**
```bash
curl -X POST http://localhost:8000/recommendations/ \
  -H "Content-Type: application/json" \
  -d '{"cart": ["Milk", "Bread"]}'
```

**Example Response (200 OK) — without LLM (no API key):**
```json
[
  {
    "product": "Greek Yogurt Plain",
    "rating": 4.1,
    "price": 5.49,
    "discount": 0,
    "why_recommended": null,
    "summary": null,
    "pros": null,
    "cons": null
  },
  {
    "product": "Cheddar Cheese Block",
    "rating": 4.6,
    "price": 6.29,
    "discount": 0,
    "why_recommended": null,
    "summary": null,
    "pros": null,
    "cons": null
  },
  {
    "product": "Free Range Eggs (12 pack)",
    "rating": 4.3,
    "price": 4.99,
    "discount": 10,
    "why_recommended": null,
    "summary": null,
    "pros": null,
    "cons": null
  }
]
```

**Example Response (200 OK) — with LLM:**
```json
[
  {
    "product": "Greek Yogurt Plain",
    "rating": 4.1,
    "price": 5.49,
    "discount": 0,
    "why_recommended": "Greek yogurt is a perfect high-protein complement to your milk and bread, great for breakfast bowls or smoothies.",
    "summary": "Customers love the thick and creamy texture, with many using it for smoothies and breakfast bowls.",
    "pros": [
      "Thick and creamy texture",
      "High protein content",
      "Great for smoothies"
    ],
    "cons": [
      "Can be sour compared to others",
      "Not as thick as expected by some"
    ]
  }
]
```

**Possible Errors:**
| Status | Description |
|--------|-------------|
| 422 | Invalid request body (validation error) |
| 500 | Failed to generate recommendations (LLM or database error) |

---

## Error Response Format

All error responses follow this structure:

```json
{
  "detail": "Human-readable error message"
}
```

For 422 validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "cart"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Recommendation Rules (Backend Logic)

The recommendation engine uses a rule-based system defined in `RECOMMENDATION_RULES`:

| Cart Item | Primary Recommendation |
|-----------|----------------------|
| Milk | Greek Yogurt, Cheddar Cheese, Free Range Eggs |
| Bread | Almond Butter, Cheddar Cheese, Free Range Eggs |
| Eggs | Organic Whole Milk, Sourdough Bread, Cheddar Cheese |
| Yogurt | Frozen Mixed Berries, Organic Bananas |
| Tomatoes | Schezwan Sauce, Sourdough Bread, Basmati Rice |
| Bananas | Frozen Mixed Berries, Greek Yogurt, Almond Butter |
| Coffee | Organic Whole Milk, Dark Chocolate Bar |
| Chocolate | Instant Coffee Granules, Organic Whole Milk |
| Rice | Schezwan Sauce, Free Range Eggs |
| Chips | Schezwan Sauce, Dark Chocolate Bar |
| Cheese | Sourdough Bread, Roma Tomatoes |
| Berries | Greek Yogurt, Organic Whole Milk |

If no rules match, the system falls back to top-rated products.

---

## Data Types

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique product identifier |
| `name` | string | Product display name |
| `category` | string | Product category (Dairy, Bakery, Produce, etc.) |
| `price` | float | Current selling price |
| `rating` | float | Average customer rating (0–5) |
| `discount` | integer | Discount percentage (0–100) |
| `image_url` | string\|null | Relative URL to product image |
| `unit` | string | Unit of measurement (e.g., "1 L", "12 pcs") |
| `reviews_count` | integer | Number of customer reviews |
| `product` | string | Recommendation product name |
| `why_recommended` | string\|null | LLM-generated explanation |
| `summary` | string\|null | LLM-generated review summary |
| `pros` | string[]\|null | LLM-extracted positive points |
| `cons` | string[]\|null | LLM-extracted negative points |