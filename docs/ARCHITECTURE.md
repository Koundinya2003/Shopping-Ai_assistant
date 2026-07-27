# Architecture Diagram

```mermaid
flowchart TD
    subgraph Frontend ["Frontend (Next.js)"]
        UI["App Shell (app-shell.tsx)"]
        Home["Home Screen (home-screen.tsx)"]
        Details["Details Screen (details-screen.tsx)"]
        Cart["Cart Screen (cart-screen.tsx)"]
        BottomNav["Bottom Navigation (bottom-nav.tsx)"]
        StoreProvider["Store Provider (store-provider.tsx)"]
        API["API Service (lib/api.ts)"]
        Products["Products Logic (lib/products.ts)"]
    end

    subgraph Backend ["Backend (FastAPI)"]
        Main["main.py<br/>CORS · Logging · Startup"]
        ProductsAPI["GET /products/<br/>(products.py)"]
        RecommendationsAPI["POST /recommendations/<br/>(recommendations.py)"]
        RecommService["Recommendation Service<br/>(services/recommendations.py)"]
        OpenRouterService["OpenRouter Service<br/>(services/openrouter.py)"]
        Database["Database Layer<br/>(database/__init__.py)"]
        Seed["Seed Data<br/>(database/seed.py)"]
    end

    subgraph Storage ["Storage"]
        SQLite[("SQLite<br/>grocery_assistant.db")]
    end

    subgraph External ["External"]
        OpenRouter["OpenRouter API<br/>(LLM Provider)"]
    end

    subgraph Prompts ["Prompt Templates"]
        SystemPrompt["SYSTEM_PROMPT (openrouter.py)"]
        ReviewSummary["review_summary.txt"]
    end

    %% Frontend flow
    UI --> StoreProvider
    StoreProvider --> Home
    StoreProvider --> Details
    StoreProvider --> Cart
    StoreProvider --> BottomNav
    StoreProvider --> API
    Products --> API

    %% API calls
    Home -.->|"fetchProducts()"| API
    Home -.->|"fetchRecommendations()"| API
    API -.->|"HTTP GET /products/"| ProductsAPI
    API -.->|"HTTP POST /recommendations/"| RecommendationsAPI

    %% Backend flow
    ProductsAPI --> Database
    RecommendationsAPI --> RecommService
    RecommService --> Database
    RecommService --> OpenRouterService
    OpenRouterService --> Prompts
    
    %% OpenRouter
    OpenRouterService -.->|"HTTP POST /chat/completions"| OpenRouter
    
    %% Database
    Database --> SQLite
    Seed --> Database

    %% Styling
    classDef frontend fill:#e1f5fe,stroke:#01579b,color:#000
    classDef backend fill:#f3e5f5,stroke:#4a148c,color:#000
    classDef storage fill:#e8f5e9,stroke:#1b5e20,color:#000
    classDef external fill:#fff3e0,stroke:#e65100,color:#000
    classDef prompts fill:#fce4ec,stroke:#880e4f,color:#000

    class UI,Home,Details,Cart,BottomNav,StoreProvider,API,Products frontend
    class Main,ProductsAPI,RecommendationsAPI,RecommService,OpenRouterService,Database,Seed backend
    class SQLite storage
    class OpenRouter external
    class SystemPrompt,ReviewSummary prompts
```

## Request Lifecycle

### Products Request
1. User opens the app → `AppShell` renders → `StoreProvider` mounts
2. `useEffect` calls `fetchProducts()` → `lib/api.ts` sends `GET /products/`
3. FastAPI route handler queries all products + review counts via SQLAlchemy
4. Returns JSON array → mapped to frontend `Product` type via `mapApiProduct()`
5. Products displayed in `HomeScreen` grid, filtered by search/category

### Recommendations Request
1. User adds items to cart → `useEffect` triggers after 500ms debounce
2. `fetchRecommendations(cartNames)` → `POST /recommendations/` with `{ cart: [...] }`
3. Backend routes to `services/recommendations.py`:
   - Matches cart items against `RECOMMENDATION_RULES` dictionary
   - Finds matching products via SQL LIKE query
   - Optionally calls OpenRouter for LLM-generated explanations
   - Falls back to rule-based reasons if LLM unavailable
4. Returns up to 3 recommendations → displayed as "AI Picks" cards

### LLM Explanation Flow
1. `RecommendationService._build_llm_explanation()` fetches reviews for the product
2. Calls `OpenRouterService.explain_recommendation()` with cart, product details, reviews
3. System prompt (hardcoded) + user prompt (dynamic) sent to OpenRouter API
4. Response parsed and validated against Pydantic `RecommendationExplanation` model
5. JSON repair (code fences, extraction) attempted on malformed responses
6. Returns structured explanation or `None` → caller uses fallback reason