# 🛒 AI Grocery Assistant

An intelligent grocery shopping companion that provides context-aware product recommendations with AI-powered explanations. Built with Next.js (frontend) and FastAPI (backend).

## Features

- **Product Browsing:** Browse 15+ grocery products with search and category filtering
- **Smart Cart:** Add/remove items, see savings, and real-time bill calculation
- **AI Picks:** Cart-aware product recommendations updated every 500ms
- **LLM Explanations:** Natural-language "why this was recommended" summaries (when API key is configured)
- **Review Analysis:** AI-generated pros/cons from customer reviews
- **Responsive Design:** Mobile-first UI with bottom navigation and sticky headers
- **Graceful Degradation:** Works perfectly with or without LLM API key

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui |
| **Backend** | Python 3, FastAPI, SQLAlchemy, SQLite |
| **LLM** | OpenRouter API (DeepSeek V3) |
| **Testing** | Pytest with httpx mocking |
| **Deployment** | Vercel (frontend), Render (backend) |

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
    └── PORTFOLIO_SUMMARY.md    # Recruiter-friendly project summary
```

See [Architecture Documentation](docs/ARCHITECTURE.md) for a detailed diagram and request flow.

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or pnpm

### Backend Setup

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

The backend starts at `http://localhost:8000`. The database is auto-seeded on first run.

### Frontend Setup

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

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | — | OpenRouter API key (LLM features) |
| `DATABASE_URL` | No | `sqlite:///./grocery_assistant.db` | Database connection string |
| `CORS_ORIGINS` | No | `http://localhost:3000,...` | Comma-separated allowed origins |
| `OPENROUTER_BASE_URL` | No | `https://openrouter.ai/api/v1` | OpenRouter API base URL |
| `OPENROUTER_MODEL` | No | `deepseek/deepseek-chat-v3` | LLM model identifier |
| `OPENROUTER_TIMEOUT` | No | `30.0` | Request timeout in seconds |
| `OPENROUTER_MAX_RETRIES` | No | `3` | Max retry attempts |
| `OPENROUTER_INITIAL_RETRY_DELAY` | No | `1.0` | Initial retry delay in seconds |
| `OPENROUTER_MAX_RETRY_DELAY` | No | `10.0` | Max retry delay in seconds |
| `OPENROUTER_BACKOFF_MULTIPLIER` | No | `2.0` | Exponential backoff multiplier |

### Frontend (`Frontend/Grocery Shopping Assistant/.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8000` | Backend API base URL |

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/products/` | GET | List all products with review counts |
| `/recommendations/` | POST | Get product recommendations for a cart |

See [API Documentation](docs/API.md) for full details.

## Testing

```bash
cd backend
source venv/bin/activate
pytest -v
```

The test suite covers:
- OpenRouter service (mocked API calls)
- Response parsing and validation
- Retry logic and error handling
- Prompt loading and formatting
- Configuration management

## Local Development

### Backend
- The server auto-reloads on file changes with `--reload`
- Interactive API docs at `http://localhost:8000/docs`
- Seed data is created automatically on first startup
- LLM features require `OPENROUTER_API_KEY` to be set

### Frontend
- Hot reload enabled by default
- Connects to backend via `NEXT_PUBLIC_API_URL`
- Product images are local static assets

## Deployment

See [Deployment Guide](docs/DEPLOYMENT.md) for:
- **Vercel:** Frontend deployment with environment variables
- **Render:** Backend deployment with SQLite considerations
- **Troubleshooting:** Common issues and solutions

## Product Management Summary

See [Portfolio Summary](docs/PORTFOLIO_SUMMARY.md) for a comprehensive project overview covering:
- The user problem and solution
- Key features and technical decisions
- AI's role vs. deterministic business logic
- Technology stack and architecture

## Future Improvements

- [ ] Persistent PostgreSQL database for production
- [ ] User authentication and personalized recommendations
- [ ] Order history and reorder functionality
- [ ] Real inventory data via Blinkit/Zepto API
- [ ] A/B testing framework for recommendation quality
- [ ] Enhanced caching (Redis) for LLM responses
- [ ] WebSocket-based real-time cart sync
- [ ] Analytics dashboard for recommendation performance

## Troubleshooting

**Backend won't start:**
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`
- Check Python version (3.11+ required)

**Frontend can't reach backend:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Ensure backend is running on the expected port
- Check CORS configuration if using a different frontend URL

**LLM features not working:**
- Verify `OPENROUTER_API_KEY` is set in `.env`
- The app falls back gracefully to rule-based explanations
- Check backend logs for retry details

## License

MIT