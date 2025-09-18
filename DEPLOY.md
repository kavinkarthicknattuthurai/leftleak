# Deployment Guide for LeftLeak

## Quick Deploy Options

### Option 1: Deploy on Render (Free Tier Available)

**Backend (Python API):**

1. Go to [Render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub account and select `leftleak` repository
4. Configure:
   - **Name**: `leftleak-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
5. Add environment variable:
   - `GOOGLE_API_KEY` = (your friend's Google Gemini API key)
6. Click "Create Web Service"

**Frontend (Next.js):**

1. Go to [Vercel.com](https://vercel.com) and sign up
2. Click "New Project"
3. Import the `leftleak` repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `web`
5. Add environment variable:
   - `PYTHON_API_URL` = (your Render backend URL, e.g., `https://leftleak-api.onrender.com`)
6. Click "Deploy"

### Option 2: Deploy on Railway (Simpler, $5/month)

1. Go to [Railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `leftleak` repository
4. Railway will auto-detect both services
5. Add environment variables:
   - For backend: `GOOGLE_API_KEY`
   - For frontend: `PYTHON_API_URL` (will be auto-generated)
6. Click "Deploy"

### Option 3: Local Deployment (Free, requires technical friend)

If your friend has a computer that can run 24/7:

**Using Docker Compose** (create `docker-compose.yml`):

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    command: python api_server.py

  frontend:
    build: ./web
    ports:
      - "3000:3000"
    environment:
      - PYTHON_API_URL=http://backend:8000
    depends_on:
      - backend
```

Then run: `docker-compose up -d`

### Option 4: Deploy on Google Cloud Run (Pay per use)

**Backend:**
```bash
# Build and deploy backend
gcloud run deploy leftleak-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY
```

**Frontend:**
```bash
cd web
gcloud run deploy leftleak-web \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars PYTHON_API_URL=https://leftleak-api-xxx.run.app
```

## Getting API Keys

Your friend needs:
1. **Google Gemini API Key**:
   - Go to [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to the deployment environment

## Estimated Costs

- **Render**: Free tier (with limitations)
- **Vercel**: Free for frontend
- **Railway**: ~$5/month
- **Google Cloud Run**: ~$0-10/month (pay per request)
- **Local**: Free (but requires always-on computer)

## Recommended: Render + Vercel

This combination is:
- Free to start
- Easy to set up
- Scalable if needed
- Professional URLs

## Post-Deployment

After deploying, your friend can access the app at:
- Frontend URL (from Vercel)
- Share the link with others!

## Need Help?

If deployment fails, check:
1. Environment variables are set correctly
2. Build logs for errors
3. API URL in frontend matches backend URL