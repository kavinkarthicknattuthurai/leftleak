'use client';

import { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface SearchBoxProps {
  onSearch: (question: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  isInitial?: boolean;
}

export default function SearchBox({ 
  onSearch, 
  isLoading = false, 
  placeholder = "Ask about leftist perspectives...",
  isInitial = true 
}: SearchBoxProps) {
  const [input, setInput] = useState('');

  const handleSubmit = () => {
    if (input.trim() && !isLoading) {
      onSearch(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={`w-full max-w-5xl mx-auto ${isInitial ? 'animate-slide-up' : ''}`}>
      <div
        className="relative rounded-3xl p-4 md:p-5 bg-white/95 backdrop-blur-md shadow-lg ring-1 ring-black/10"
      >
        <div className="flex gap-4 items-start">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={isLoading}
            className="flex-1 resize-none bg-transparent border-0 outline-none text-gray-900 placeholder:text-gray-500 text-lg md:text-xl leading-[1.6] caret-gray-900"
            rows={1}
            style={{ minHeight: '36px', maxHeight: '200px' }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = 'auto';
              target.style.height = target.scrollHeight + 'px';
            }}
          />
          <button
            onClick={handleSubmit}
            disabled={isLoading || !input.trim()}
            className={`
              shrink-0 px-5 py-4 rounded-2xl transition-all duration-150
              ${isLoading || !input.trim() 
                ? 'bg-gray-200 text-gray-500 cursor-not-allowed' 
                : 'bg-gradient-to-r from-pink-500 to-purple-600 text-white hover:opacity-95 active:scale-95'
              }
            `}
            aria-label="Send"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
