# Running LeftLeak Application

This application consists of two parts:
1. Python backend API server (FastAPI)
2. Next.js frontend web application

## Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API key (in .env file)

## Setup Instructions

### 1. Install Python Dependencies

First, ensure you're in the project root directory and install the Python dependencies:

```bash
# If you have a virtual environment
.venv\Scripts\activate  # On Windows
# or
source .venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Python Backend Server

In the project root directory, run:

```bash
python api_server.py
```

The API server will start on http://localhost:8000

You can test it by visiting:
- http://localhost:8000 (health check)
- http://localhost:8000/docs (API documentation)

### 3. Start the Next.js Frontend

In a new terminal, navigate to the web folder:

```bash
cd web
npm install  # If you haven't already
npm run dev
```

The web application will start on http://localhost:3000

## Using the Application

1. Open http://localhost:3000 in your browser
2. You'll see the LeftLeak interface with a rainbow-themed background
3. Type your question about leftist perspectives in the search box
4. Press Enter or click the send button
5. The app will query Bluesky for relevant posts and present a summary
6. Click on follow-up questions to explore topics further

## Features

- **Modern UI**: Inspired by ChatGPT and Perplexity with smooth animations
- **LGBTQ+ Theme**: Rainbow gradients and progressive branding
- **Real-time Search**: Queries Bluesky's Jetstream for fresh content
- **Source Attribution**: All responses include links to original Bluesky posts
- **Follow-up Questions**: Smart suggestions based on topic context
- **Glass Morphism**: Modern translucent UI effects

## Troubleshooting

If the frontend shows "trouble connecting to Bluesky data source":
1. Make sure the Python backend is running on port 8000
2. Check that your .env file has valid API keys
3. Ensure no firewall is blocking localhost connections

## Development

- Frontend code: `web/src/app/page.tsx` and components in `web/src/components/`
- Backend API: `api_server.py`
- Original RAG logic: `simple_rag/` folder