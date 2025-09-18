# LeftLeak - What the Left Actually Thinks

A web application that aggregates and presents real leftist opinions from Bluesky, providing insights into progressive perspectives on various topics.

![LeftLeak Screenshot](screenshot.png)

## Overview

LeftLeak is a research tool that uses AI to analyze and summarize leftist viewpoints from Bluesky posts. It provides real-time insights into what progressives are actually saying about current events, politics, and social issues.

## Features

- 🔍 **Real-time Search**: Query any topic and get summaries of leftist perspectives
- 📊 **Authentic Sources**: All responses cite actual Bluesky users with @handles
- 🎨 **Modern UI**: Clean, responsive interface with smooth animations
- ⚡ **Fast Retrieval**: Hybrid search combining vector embeddings and live streaming
- 🌈 **Progressive Design**: LGBTQ+ themed aesthetics with accessibility in mind

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - API server
- **Google Gemini AI** - Text generation and embeddings
- **ChromaDB** - Vector database for semantic search
- **Bluesky API** - Data source via AT Protocol

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Lucide Icons** - Icon library

## Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API key
- Bluesky account (optional, for authenticated features)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/kavinkarthicknattuthurai/leftleak.git
cd leftleak
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.template .env
# Edit .env and add your Google Gemini API key:
# GOOGLE_API_KEY=your_api_key_here
```

### 3. Frontend Setup

```bash
cd web
npm install
```

## Running the Application

### 1. Start the Backend API

```bash
# From project root
python api_server.py
```

The API will be available at http://localhost:8000

### 2. Start the Frontend

```bash
# In a new terminal
cd web
npm run dev
```

The web app will be available at http://localhost:3000

## Usage

1. Visit http://localhost:3000
2. Enter a topic or question in the search box
3. View aggregated leftist perspectives with source citations
4. Click on source links to see original Bluesky posts

## API Endpoints

- `POST /api/query` - Submit a question and get leftist perspectives
- `GET /api/status` - Check system status and configuration

## Architecture

The application uses a RAG (Retrieval Augmented Generation) approach:

1. **Data Ingestion**: Streams posts from Bluesky's Jetstream
2. **Embedding**: Converts posts to vector embeddings using Gemini
3. **Storage**: Stores in ChromaDB for fast semantic search
4. **Retrieval**: Finds relevant posts using hybrid search
5. **Generation**: Summarizes perspectives using Gemini LLM
6. **Citation**: Links back to original Bluesky posts

## Development

### Project Structure

```
leftleak/
├── api_server.py        # FastAPI backend server
├── simple_rag/          # RAG implementation
│   ├── config.py        # Configuration
│   ├── rag.py          # Main RAG logic
│   ├── database.py     # ChromaDB wrapper
│   └── ingest.py       # Bluesky data ingestion
├── web/                # Next.js frontend
│   ├── src/
│   │   ├── app/        # App router pages
│   │   └── components/ # React components
│   └── public/         # Static assets
└── requirements.txt    # Python dependencies
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Bluesky team for the AT Protocol
- Google for Gemini AI
- The progressive community on Bluesky for their perspectives

## Disclaimer

This tool aggregates publicly available social media posts. Views presented are from individual users and do not represent any official positions.