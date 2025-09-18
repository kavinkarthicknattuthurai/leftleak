'use client';

import { useState, useEffect, useRef } from 'react';
import Image from 'next/image';
import { v4 as uuidv4 } from 'uuid';
import SearchBox from '@/components/SearchBox';
import MessageDisplay from '@/components/MessageDisplay';
import LoadingAnimation from '@/components/LoadingAnimation';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamp: Date;
}

const rotatingLines = [
  'Aggregating real leftist opinions from Bluesky',
  'See what progressives are actually saying',
  'Data sourced from thousands of Bluesky posts',
  'Real views from real people on the left',
  'Understanding the progressive perspective'
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasInteracted, setHasInteracted] = useState(false);
  const [lineIndex, setLineIndex] = useState(0);
  const messagesRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const id = setInterval(() => {
      setLineIndex((i) => (i + 1) % rotatingLines.length);
    }, 2600);
    return () => clearInterval(id);
  }, []);

  const handleSearch = async (question: string) => {
    if (!hasInteracted) setHasInteracted(true);

    const userMessage: Message = {
      id: uuidv4(),
      type: 'user',
      content: question,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Ensure we stay on the same screen and reveal messages area
    setTimeout(() => {
      messagesRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();

      if (response.ok) {
        const assistantMessage: Message = {
          id: uuidv4(),
          type: 'assistant',
          content: data.answer,
          sources: data.sources,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errorMessage: Message = {
          id: uuidv4(),
          type: 'assistant',
          content: 'Sorry, something went wrong. Please try again.',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: uuidv4(),
        type: 'assistant',
        content: 'Network error. Please check your connection and try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Image */}
      <div className="fixed inset-0 -z-10">
        <Image
          src="/dp.webp"
          alt="Background"
          fill
          className="object-cover opacity-20"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-b from-white/90 via-white/85 to-white/90" />
      </div>

      {/* Main Content */}
      <div className="min-h-screen flex flex-col justify-between">
        {/* Hero (centered first view, shrinks after first prompt) */}
        <section className={`px-6 pt-8 ${hasInteracted ? 'pb-4' : 'hero hero--center'}`}>
          <div className="max-w-4xl mx-auto text-center animate-fade-in px-4">
            <h2 className={`font-extrabold tracking-tight text-gray-900 ${hasInteracted ? 'text-3xl md:text-4xl mb-2' : 'text-5xl md:text-6xl mb-3'} transition-all duration-500`}>
              What the Left Actually Thinks
            </h2>
            {!hasInteracted && (
              <p className="text-base md:text-lg text-gray-600 mb-6">
                Real views from real leftists on Bluesky
              </p>
            )}

            <div>
              <SearchBox
                onSearch={handleSearch}
                isLoading={isLoading}
                placeholder={hasInteracted ? "Ask another question..." : "What are progressives saying about..."}
                isInitial={!hasInteracted}
              />
            </div>

            {!hasInteracted && (
              <div className="mt-4 h-6 overflow-hidden">
                <p key={lineIndex} className="text-sm md:text-base text-gray-800 animate-slide-up">
                  {rotatingLines[lineIndex]}
                </p>
              </div>
            )}
          </div>
        </section>

        {/* Messages Area */}
        <main className="flex-1 px-6 py-4">
          <div ref={messagesRef} className="max-w-4xl mx-auto space-y-6 pb-6">
            {messages.map((message) => (
              <MessageDisplay key={message.id} message={message} />
            ))}
            {isLoading && <LoadingAnimation />}
          </div>
        </main>
      </div>
    </div>
  );
}
