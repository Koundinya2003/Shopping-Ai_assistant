# Deployment Guide

## Vercel (Frontend)

### Prerequisites
- A Vercel account
- Your frontend code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

### Environment Variables

Set the following in Vercel project settings → Environment Variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend.onrender.com` | Backend API base URL |

### Build Configuration

| Setting | Value |
|---------|-------|
| **Framework Preset** | Next.js |
| **Build Command** | `npm run build` (or `pnpm build`) |
| **Output Directory** | `.next` (default) |
| **Install Command** | `npm install` (or `pnpm install`) |
| **Node Version** | 20.x (default) |

### Deployment Steps

1. **Connect Repository:**
   - Go to [vercel.com](https://vercel.com) → Add New Project
   - Import your Git repository
   - Select the `Frontend/Grocery Shopping Assistant` directory as the root

2. **Configure Project:**
   - Framework Preset: Next.js (auto-detected)
   - Root Directory: `Frontend/Grocery Shopping Assistant`
   - Build Command: Keep default
   - Output Directory: Keep default

3. **Add Environment Variables:**
   - Add `NEXT_PUBLIC_API_URL` pointing to your Render backend URL

4. **Deploy:**
   - Click "Deploy"
   - Vercel will automatically build and deploy
   - Each push to the main branch triggers a new deployment

### Post-Deployment
- Verify the app loads at the Vercel-provided URL
- Test API connectivity by checking product loading
- Configure a custom domain if needed (Settings → Domains)

---

## Render (Backend)

### Prerequisites
- A Render account
- Your backend code pushed to a Git repository

### Environment Variables

Set the following in Render dashboard → Web Service → Environment:

| Variable | Required | Value | Description |
|----------|----------|-------|-------------|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key | For LLM features |
| `DATABASE_URL` | No | `sqlite:///./grocery_assistant.db` | SQLite path (default) |
| `CORS_ORIGINS` | No | `https://your-frontend.vercel.app` | Allowed origins |
| `OPENROUTER_MODEL` | No | `deepseek/deepseek-chat-v3` | LLM model |
| `OPENROUTER_TIMEOUT` | No | `30.0` | Request timeout |
| `OPENROUTER_MAX_RETRIES` | No | `3` | Max retry attempts |

### Build & Start Commands

| Setting | Value |
|---------|-------|
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### SQLite Considerations

**Important:** Render's ephemeral filesystem means the SQLite database file will be **deleted on every deploy/restart**. The seed script runs on startup and will repopulate the database automatically.

For production with persistent data, consider:
- Upgrading to a managed PostgreSQL database (Render offers this)
- Changing `DATABASE_URL` to a PostgreSQL connection string
- The codebase uses SQLAlchemy, so switching databases requires minimal changes

### Deployment Steps

1. **Create Web Service:**
   - Go to [render.com](https://render.com) → Dashboard → New + → Web Service
   - Connect your Git repository

2. **Configure Service:**
   - Name: `grocery-assistant-api`
   - Root Directory: Leave as root (the backend is at `backend/`)
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables:**
   - Add all required variables from the table above
   - Set `CORS_ORIGINS` to your Vercel frontend URL

4. **Select Plan:**
   - Free tier works for development/demo
   - Starter or higher for production (avoids spin-down)

5. **Deploy:**
   - Click "Create Web Service"
   - Render will build and deploy automatically

### Post-Deployment
- Verify the health endpoint: `https://your-app.onrender.com/`
- Test products endpoint: `https://your-app.onrender.com/products/`
- Update `NEXT_PUBLIC_API_URL` on Vercel to point to this URL

---

## Environment Files

### Backend (`backend/.env.example`)
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
# OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
# OPENROUTER_MODEL=deepseek/deepseek-chat-v3
# OPENROUTER_TIMEOUT=30.0
# OPENROUTER_MAX_RETRIES=3
# OPENROUTER_INITIAL_RETRY_DELAY=1.0
# OPENROUTER_MAX_RETRY_DELAY=10.0
# OPENROUTER_BACKOFF_MULTIPLIER=2.0
DATABASE_URL=sqlite:///./grocery_assistant.db
# CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (`Frontend/Grocery Shopping Assistant/.env.local.example`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Troubleshooting

### Backend won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that `OPENROUTER_API_KEY` is set (optional but warned at startup)
- Verify the database path is writable

### Frontend can't reach backend
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify CORS origins include the frontend URL
- Ensure the backend is running and accessible

### Database resets on Render
- This is expected with SQLite on Render's ephemeral storage
- The seed script repopulates data on each startup
- For persistent data, migrate to PostgreSQL

### LLM features not working
- Verify `OPENROUTER_API_KEY` is set correctly
- Check OpenRouter service status
- The system falls back to rule-based explanations gracefully