# AI Grocery Assistant — Product Management Portfolio Summary

## The Problem

Online grocery shopping feels overwhelming. With hundreds of products to choose from, customers often miss complementary items, waste time browsing, and experience decision fatigue. Traditional e-commerce recommendation systems are either too generic ("customers also bought") or require extensive manual curation.

## The Solution

**AI Grocery Assistant** is an intelligent shopping companion that provides context-aware product recommendations based on what's in the user's cart. It combines deterministic business logic (rule-based product pairings) with optional LLM-powered natural language explanations, delivering a curated "AI Picks" section that feels personal and helpful.

## Key Features

- **Smart Product Discovery:** Browse 15+ grocery products with real-time search and category filtering
- **AI Picks Recommendations:** Cart-aware suggestions updated in real-time as items are added or removed
- **LLM-Enhanced Explanations:** When configured, generates natural-language "why this was recommended" summaries from customer reviews
- **Review Sentiment Analysis:** Extracts pros and cons from aggregated customer reviews
- **Responsive Mobile-First UI:** Optimized for mobile shopping with a fast, app-like experience

## Technical Architecture

The system follows a clean client-server architecture:

- **Frontend:** Next.js 16 with TypeScript, React Context for state management, and Tailwind CSS for styling
- **Backend:** FastAPI (Python) with SQLAlchemy ORM and SQLite
- **LLM Integration:** OpenRouter API gateway for flexible model selection (DeepSeek V3 by default)
- **Key Design Patterns:** Context provider pattern, service layer abstraction, fail-soft LLM fallbacks

## Product Decisions

1. **Hybrid Recommendation Engine:** Rather than relying purely on AI, we built a deterministic rule-based system for product matching, layered with AI for explanatory text. This ensures recommendations are always relevant (even without an API key) while AI adds delight when available.

2. **Fallback-First AI Integration:** Every LLM call has a fallback — if the API is down, slow, or returns bad JSON, the system degrades gracefully with rule-based explanations. No broken user experiences.

3. **SQLite for MVP:** Chose SQLite over PostgreSQL to minimize setup complexity. The seed script auto-populates data on first run, making local development instant.

4. **Mobile-First, Not Mobile-Only:** Designed as a mobile web app with a bottom nav, sticky headers, and touch-friendly interactions, while maintaining full desktop usability.

## AI's Role vs. Deterministic Logic

| Component | Approach | Why |
|-----------|----------|-----|
| Product Matching | Deterministic (rule-based dictionary) | Guarantees relevant, curated pairings |
| Recommendation Explanations | LLM-powered with fallback | Adds personalization and trust |
| Review Summaries | LLM-powered with fallback | Saves users from reading dozens of reviews |
| Product Search | Deterministic (filter + regex) | Instant, predictable results |
| Cart Logic | Deterministic (React state) | Fast, offline-capable |

## Measurable Product Value

- **Instant Onboarding:** No sign-up required — just open and shop
- **Reduced Decision Time:** AI Picks surface relevant additions immediately
- **Graceful Degradation:** Works perfectly with or without AI, ensuring 100% uptime
- **Developer Experience:** Single `uvicorn` command starts the entire backend; frontend runs with `npm run dev`

## Technologies Used

**Frontend:** Next.js 16, TypeScript, React 19, Tailwind CSS v4, Heroicons, shadcn/ui  
**Backend:** Python 3, FastAPI, SQLAlchemy, SQLite, Pydantic  
**AI/ML:** OpenRouter API (DeepSeek V3), structured output parsing  
**Testing:** Pytest with httpx mocking  
**Deployment:** Vercel (frontend), Render (backend)