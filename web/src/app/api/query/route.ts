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

    // For Vercel demo deployment, we'll use mock data
    // In production, this would connect to the Python backend
    
    // Generate mock leftist responses based on keywords
    const mockResponses: Record<string, any> = {
      'abortion': {
        answer: `This is what leftists on Bluesky are actually saying about abortion rights:

Progressives on Bluesky strongly support reproductive rights and bodily autonomy. **@reprorightsactivist.bsky.social** argues that "abortion is healthcare and a fundamental human right." Many users express concern about restrictive state laws.

**@feministvoice.bsky.social** highlights the disproportionate impact on marginalized communities: "Poor women and women of color are most affected by abortion bans."

There's widespread support for expanding access to reproductive healthcare and protecting providers from harassment.`,
        sources: [
          'https://bsky.app/profile/reprorightsactivist.bsky.social/post/abc123',
          'https://bsky.app/profile/feministvoice.bsky.social/post/def456'
        ]
      },
      'climate': {
        answer: `This is what leftists on Bluesky are actually saying about climate change:

**@climateactivist.bsky.social** emphasizes urgent action: "We have less than a decade to prevent catastrophic warming. The time for incremental change is over."

Many progressives call for a Green New Deal. **@ecosocialist.bsky.social** states: "We need massive public investment in renewable energy and a just transition for workers."

There's strong criticism of fossil fuel companies, with **@envjustice.bsky.social** noting: "Oil executives knew about climate change for decades and funded disinformation campaigns."`,
        sources: [
          'https://bsky.app/profile/climateactivist.bsky.social/post/ghi789',
          'https://bsky.app/profile/ecosocialist.bsky.social/post/jkl012'
        ]
      },
      'default': {
        answer: `This is what leftists on Bluesky are actually saying about "${question}":

Progressive voices on Bluesky emphasize social justice, equality, and systemic change. **@leftistvoice.bsky.social** argues for "addressing root causes of inequality rather than surface-level reforms."

**@progressive.bsky.social** highlights the importance of intersectionality: "We can't separate issues of race, class, gender, and sexuality - they're all interconnected."

Many users express frustration with moderate approaches and call for bold, transformative policies.`,
        sources: [
          'https://bsky.app/profile/leftistvoice.bsky.social/post/mno345',
          'https://bsky.app/profile/progressive.bsky.social/post/pqr678'
        ]
      }
    };
    
    // Simple keyword matching
    let response = mockResponses.default;
    const lowerQuestion = question.toLowerCase();
    
    if (lowerQuestion.includes('abortion') || lowerQuestion.includes('reproductive')) {
      response = mockResponses.abortion;
    } else if (lowerQuestion.includes('climate') || lowerQuestion.includes('environment')) {
      response = mockResponses.climate;
    }
    
    // Add a small delay to simulate processing
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return NextResponse.json({
      answer: response.answer,
      sources: response.sources,
      context_used: 5,
      followUpQuestions: []
    });
  } catch (error) {
    console.error('Query API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}