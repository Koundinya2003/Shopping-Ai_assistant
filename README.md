<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/readme/01_hero_dark.svg">
  <img src="docs/readme/01_hero_light.svg" width="100%" alt="AI Grocery Assistant: your cart, read back to you. An intelligent grocery shopping companion that looks at what is in your cart and suggests what goes with it, with a plain language reason for every pick. Rules choose the products, an LLM explains and ranks them, and the app works with or without an API key. Built with Next.js and FastAPI. Animated example: a cart with Organic Whole Milk; the assistant answers with Greek Yogurt Plain, confidence 92, a protein rich breakfast pairing; Cheddar Cheese Block, confidence 85, a classic dairy combination; and Free Range Eggs, because milk and eggs are breakfast staples. Numbers: 15 products, 147 seeded reviews, 13 cart pairing rules, 3 AI Picks per cart, 52 backend tests.">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/readme/02_pipeline_dark.svg">
  <img src="docs/readme/02_pipeline_light.svg" width="100%" alt="How a pick is made, in six steps. 1. The cart changes, and after a 500 ms debounce the front end posts the cart names to POST /recommendations/. 2. Rule match: each cart item is matched against RECOMMENDATION_RULES, 13 cart keys each with 3 pairings, and products are found with a SQL LIKE query, skipping anything already in the cart. 3. The top 5 candidates are kept. 4. Cache: an MD5 key of the sorted cart and candidate ids, kept for 5 minutes, so the same cart never pays for the same LLM call twice. 5. The LLM, DeepSeek V3 through OpenRouter, ranks and enriches the candidates with confidence, why, when, best for, review summary, pros and cons, using customer reviews. 6. The top 3 come back as AI Picks. Cart keys: Milk, Bread, Eggs, Yogurt, Tomatoes, Bananas, Coffee, Chocolate, Rice, Chips, Cheese, Butter, Berries. Example pairings: Bread to Almond Butter, Rice to Schezwan Sauce, Chips to Sparkling Water Lime.">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/readme/03_fallback_dark.svg">
  <img src="docs/readme/03_fallback_light.svg" width="100%" alt="Fallback first: the shopper never sees an error. Tier 1, AI ranking: the model ranks and enriches the top candidates and successful responses are cached. Tier 2, when ranking fails: rule based picks, each with its own LLM explanation built from customer reviews. Tier 3, final fallback: rule based picks with hand written reasons, which always returns valid recommendations; an empty cart match falls back to top rated products. Each OpenRouter call has a 30 second timeout and up to 3 retries with exponential backoff: 1 second, then 2, then 4, capped at 10 seconds. Malformed JSON is repaired, for example by stripping code fences, before validation with Pydantic. AI versus deterministic: product matching is a rule based dictionary; recommendation explanations and review summaries are LLM powered with a fallback; product search is filter and regex; cart logic is React state.">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/readme/04_pick_card_dark.svg">
  <img src="docs/readme/04_pick_card_light.svg" width="100%" alt="Anatomy of an AI pick, from the sample response in the docs. Greek Yogurt Plain, confidence 92 out of 100. Why: customers buying milk frequently add Greek yogurt for a protein rich breakfast, and reviews highlight the creamy texture. When: for weekday breakfasts. Best for: health conscious families. Pros: high in protein, creamy texture, good value for money. Cons: slightly tangy taste, shorter shelf life than expected. Confidence colors: 90 to 100 green for high, 70 to 89 yellow for medium, below 70 red for low. Seeded review sentiment across 147 reviews: 112 positive, 21 neutral, 14 negative. Trust features: an expandable reasoning card, a confidence indicator, a review sentiment summary, a recommendation type badge with 7 types such as Frequently Bought Together and Meal Companion, an AI insights panel showing what was analysed, an informative empty state, and thumbs up or down feedback stored in localStorage.">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/readme/05_stack_dark.svg">
  <img src="docs/readme/05_stack_light.svg" width="100%" alt="Stack, API and what is next. Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS v4 and shadcn/ui, mobile first with bottom navigation. Backend: Python 3, FastAPI, SQLAlchemy and SQLite, auto seeded on first run. LLM: OpenRouter API with DeepSeek V3. Testing: Pytest with httpx mocking. Deployment: Vercel for the frontend and Render for the backend. Endpoints: GET / health check, GET /products/ lists all products with review counts, POST /recommendations/ returns picks for a cart. Run: in backend, pip install the requirements and run uvicorn app.main:app with reload on port 8000; in the frontend folder, npm install and npm run dev on port 3000. Future improvements: PostgreSQL for production, user accounts and personalised picks, order history and reorder, real inventory data, A/B testing of recommendation quality, Redis caching for LLM responses, WebSocket cart sync, and an analytics dashboard.">
</picture>

# AI Grocery Assistant

An intelligent grocery shopping companion that provides context aware product recommendations with AI powered explanations. Built with Next.js (frontend) and FastAPI (backend).

## Features

* **Product browsing:** browse 15 grocery products with search and category filtering
* **Smart cart:** add and remove items, see savings, and real time bill calculation
* **AI Picks:** cart aware product recommendations, refreshed 500 ms after the cart changes
* **LLM explanations:** natural language "why this was recommended" summaries (when an API key is configured)
* **Review analysis:** AI generated pros and cons from customer reviews
* **Responsive design:** mobile first UI with bottom navigation and sticky headers
* **Graceful degradation:** works with or without an LLM API key

## Tech stack

* **Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui
* **Backend:** Python 3, FastAPI, SQLAlchemy, SQLite
* **LLM:** OpenRouter API (DeepSeek V3)
* **Testing:** Pytest with httpx mocking
* **Deployment:** Vercel (frontend), Render (backend)

## Architecture

```
blinkit-ai-assistant/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── api/                # Route handlers (products, recommendations)
│   │   ├── database/           # DB connection, session, seed data
│   │   ├── models/             # SQLAlchemy ORM models (Product, Review)
│   │   ├── prompts/            # LLM prompt templates
│   │   ├── services/           # Business logic (recommendations, OpenRouter)
│   │   └── main.py             # FastAPI app, CORS, startup
│   ├── tests/                  # Pytest unit tests
│   ├── requirements.txt
│   └── .env.example
├── Frontend/Grocery Shopping Assistant/
│   ├── app/                    # Next.js app router (layout, pages)
│   ├── components/
│   │   ├── store/              # Store components (screens, cards, nav)
│   │   └── ui/                 # Reusable UI components (button)
│   ├── lib/                    # API client, product mapping, utilities
│   ├── public/                 # Static assets (images)
│   ├── .env.local.example
│   └── package.json
└── docs/                       # Documentation
    ├── ARCHITECTURE.md         # Architecture diagram and request lifecycle
    ├── API.md                  # Full API documentation
    ├── DEPLOYMENT.md           # Vercel + Render deployment guide
    └── PORTFOLIO_SUMMARY.md    # Recruiter friendly project summary
```

See the [Architecture documentation](docs/ARCHITECTURE.md) for a detailed diagram and request flow. More background lives in [`docs/AI_RECOMMENDATION_ENGINE_REPORT.md`](docs/AI_RECOMMENDATION_ENGINE_REPORT.md), [`docs/AI_TRANSPARENCY_FEATURES.md`](docs/AI_TRANSPARENCY_FEATURES.md) and [`docs/PRODUCTION_READINESS_REPORT.md`](docs/PRODUCTION_READINESS_REPORT.md).

## Installation

### Prerequisites

* Python 3.11 or newer
* Node.js 18 or newer
* npm or pnpm

### Backend setup

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env and add your OpenRouter API key (optional)

# Start the server
uvicorn app.main:app --reload
```

The backend starts at `http://localhost:8000`. The database is seeded automatically on first run.

### Frontend setup

```bash
# Navigate to the frontend directory
cd "Frontend/Grocery Shopping Assistant"

# Install dependencies
npm install
# or
pnpm install

# Copy and configure environment variables
cp .env.local.example .env.local

# Start the development server
npm run dev
# or
pnpm dev
```

The frontend starts at `http://localhost:3000`.

## Environment variables

### Backend (`backend/.env`)

<table>
<tr><th>Variable</th><th>Required</th><th>Default</th><th>Description</th></tr>
<tr><td><code>OPENROUTER_API_KEY</code></td><td>Yes (for LLM features)</td><td>none</td><td>OpenRouter API key</td></tr>
<tr><td><code>DATABASE_URL</code></td><td>No</td><td><code>sqlite:///./grocery_assistant.db</code></td><td>Database connection string</td></tr>
<tr><td><code>CORS_ORIGINS</code></td><td>No</td><td><code>http://localhost:3000,...</code></td><td>Comma separated allowed origins</td></tr>
<tr><td><code>OPENROUTER_BASE_URL</code></td><td>No</td><td><code>https://openrouter.ai/api/v1</code></td><td>OpenRouter API base URL</td></tr>
<tr><td><code>OPENROUTER_MODEL</code></td><td>No</td><td><code>deepseek/deepseek-chat-v3</code></td><td>LLM model identifier</td></tr>
<tr><td><code>OPENROUTER_TIMEOUT</code></td><td>No</td><td><code>30.0</code></td><td>Request timeout in seconds</td></tr>
<tr><td><code>OPENROUTER_MAX_RETRIES</code></td><td>No</td><td><code>3</code></td><td>Max retry attempts</td></tr>
<tr><td><code>OPENROUTER_INITIAL_RETRY_DELAY</code></td><td>No</td><td><code>1.0</code></td><td>Initial retry delay in seconds</td></tr>
<tr><td><code>OPENROUTER_MAX_RETRY_DELAY</code></td><td>No</td><td><code>10.0</code></td><td>Max retry delay in seconds</td></tr>
<tr><td><code>OPENROUTER_BACKOFF_MULTIPLIER</code></td><td>No</td><td><code>2.0</code></td><td>Exponential backoff multiplier</td></tr>
</table>

### Frontend (`Frontend/Grocery Shopping Assistant/.env.local`)

<table>
<tr><th>Variable</th><th>Required</th><th>Default</th><th>Description</th></tr>
<tr><td><code>NEXT_PUBLIC_API_URL</code></td><td>No</td><td><code>http://localhost:8000</code></td><td>Backend API base URL</td></tr>
</table>

## API overview

* `GET /`: health check
* `GET /products/`: list all products with review counts
* `POST /recommendations/`: get product recommendations for a cart

See the [API documentation](docs/API.md) for full details.

## Testing

```bash
cd backend
source venv/bin/activate
pytest -v
```

The test suite covers:

* OpenRouter service (mocked API calls)
* Response parsing and validation
* Retry logic and error handling
* Prompt loading and formatting
* Configuration management
* Recommendation caching, AI ranking and fallback behaviour

## Local development

**Backend**

* The server reloads on file changes with `--reload`
* Interactive API docs at `http://localhost:8000/docs`
* Seed data is created automatically on first startup
* LLM features require `OPENROUTER_API_KEY` to be set

**Frontend**

* Hot reload is enabled by default
* Connects to the backend via `NEXT_PUBLIC_API_URL`
* Product images are local static assets

## Deployment

See the [Deployment guide](docs/DEPLOYMENT.md) for:

* **Vercel:** frontend deployment with environment variables
* **Render:** backend deployment with SQLite considerations
* **Troubleshooting:** common issues and solutions

## Product management summary

See the [Portfolio summary](docs/PORTFOLIO_SUMMARY.md) for a full project overview covering:

* The user problem and solution
* Key features and technical decisions
* AI's role versus deterministic business logic
* Technology stack and architecture

## Future improvements

* [ ] Persistent PostgreSQL database for production
* [ ] User authentication and personalized recommendations
* [ ] Order history and reorder functionality
* [ ] Real inventory data via Blinkit or Zepto API
* [ ] A/B testing framework for recommendation quality
* [ ] Enhanced caching (Redis) for LLM responses
* [ ] WebSocket based real time cart sync
* [ ] Analytics dashboard for recommendation performance

## Troubleshooting

**Backend won't start:**

* Ensure the virtual environment is activated
* Install dependencies: `pip install -r requirements.txt`
* Check the Python version (3.11 or newer required)

**Frontend can't reach the backend:**

* Verify `NEXT_PUBLIC_API_URL` is set correctly
* Ensure the backend is running on the expected port
* Check the CORS configuration if using a different frontend URL

**LLM features not working:**

* Verify `OPENROUTER_API_KEY` is set in `.env`
* The app falls back gracefully to rule based explanations
* Check the backend logs for retry details

## Rebuilding the panels

The images at the top are generated. Edit `docs/readme/one_sheet.html`, then run:

```bash
node docs/readme/build_readme_svgs.js docs/readme/one_sheet.html docs/readme 960
```

This needs Node with Playwright and curl (fonts are fetched from Google Fonts and embedded).

## License

MIT.
