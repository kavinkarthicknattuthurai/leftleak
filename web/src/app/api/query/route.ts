import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { question } = await request.json();

    if (!question || typeof question !== 'string') {
      return NextResponse.json(
        { error: 'Question is required' },
        { status: 400 }
      );
    }

    // Call the Python backend API
    const backendUrl = process.env.PYTHON_API_URL || 'http://localhost:8000';
    
    try {
      const response = await fetch(`${backendUrl}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error(`Backend responded with status: ${response.status}`);
      }

      const data = await response.json();
      return NextResponse.json(data);
      
    } catch (backendError) {
      console.error('Backend API error:', backendError);
      
      // Fallback to mock data if backend is not available
      const mockResponse = {
        answer: `I'm having trouble connecting to the Bluesky data source right now. Please make sure the backend server is running on port 8000.\n\nTo start the backend:\n1. Navigate to the project root\n2. Run: python api_server.py\n\nFor testing, here's a simulated response about "${question}"...`,
        sources: [
          'https://bsky.app/profile/example.bsky.social/post/demo123'
        ],
        context_used: 0,
        followUpQuestions: [
          "What are the policy implications?",
          "How does this affect marginalized communities?",
          "What's the historical context?",
          "What are activists saying about this?"
        ]
      };

      return NextResponse.json(mockResponse);
    }
  } catch (error) {
    console.error('Query API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}