# 🚀 Free Deployment Guide - Get LeftLeak Live in 10 Minutes

This guide will help you deploy LeftLeak completely free using Render (backend) + Vercel (frontend).

## Step 1: Deploy Backend on Render (5 minutes)

1. **Sign up at Render**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub and select `leftleak` repository
   - Fill in:
     - **Name**: `leftleak-api`
     - **Environment**: `Python`
     - **Build Command**: (leave as detected)
     - **Start Command**: (leave as detected)

3. **Add Your API Key**
   - Scroll to "Environment Variables"
   - Add: `GOOGLE_API_KEY` = `your-actual-gemini-api-key-here`
   - Click "Create Web Service"

4. **Wait for Deploy**
   - Takes 5-10 minutes first time
   - Copy your backend URL (like `https://leftleak-api.onrender.com`)

## Step 2: Deploy Frontend on Vercel (5 minutes)

1. **Sign up at Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Import Project**
   - Click "New Project"
   - Import `leftleak` repository
   - Root Directory: leave as is

3. **Add Environment Variable**
   - Add: `NEXT_PUBLIC_API_URL` = `your-render-backend-url`
   - Example: `https://leftleak-api.onrender.com`

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes

## 🎉 Done! Your app is live!

- Frontend URL: `https://your-app.vercel.app`
- Share this link with your 10-15 friends!

## Important Notes

- **Free Tier Limits**: Render free tier spins down after 15 mins of inactivity
- **First Request**: May take 30 seconds to wake up
- **Perfect for**: Small group of friends using it occasionally
- **Embedding Storage**: Your ChromaDB embeddings persist between requests

## Your API Keys are Safe

- Only you have access to the API keys in Render dashboard
- They're not visible in the code or to users
- Your embeddings database is private to your instance

## Troubleshooting

If the app shows demo data:
1. Check that `NEXT_PUBLIC_API_URL` in Vercel matches your Render URL
2. Make sure Render backend shows "Live" status
3. First request after sleep takes 30 seconds - be patient!

## Need Help?

- Render free tier: 750 hours/month (plenty for your use)
- Vercel free tier: Unlimited for personal projects
- Both services have great free support