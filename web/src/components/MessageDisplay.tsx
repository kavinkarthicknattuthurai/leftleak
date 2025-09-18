'use client';

import { User, Megaphone, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamp: Date;
}

interface MessageDisplayProps {
  message: Message;
}

export default function MessageDisplay({ message }: MessageDisplayProps) {
  const isUser = message.type === 'user';

  return (
    <div className={`animate-slide-up ${isUser ? 'mb-6' : 'mb-8'}`}>
      <div className={`max-w-4xl mx-auto ${isUser ? 'flex justify-end' : ''}`}>
        <div className={`${isUser ? 'max-w-2xl' : 'w-full'}`}>
          {/* User Message */}
          {isUser ? (
            <div className="flex gap-3 justify-end">
              <div className="rounded-2xl px-5 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white shadow-md">
                <p className="text-base leading-relaxed">{message.content}</p>
              </div>
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                  <User className="w-5 h-5 text-gray-600" />
                </div>
              </div>
            </div>
          ) : (
            /* Assistant Message */
            <div>
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center shadow-lg">
                    <Megaphone className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="glass-morphism rounded-2xl px-6 py-4">
                    <div className="prose prose-base max-w-none">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => {
                            // Process text to bold @usernames and italicize #hashtags only
                            const processText = (text: unknown): React.ReactNode => {
                              if (typeof text !== 'string') return text;
                              
                              // Match @usernames and #hashtags
                              const patterns = /(@\w+\.bsky\.social|@\w+|#\w+)/g;
                              
                              const parts = text.split(patterns);
                              
                              return parts.map((part, index) => {
                                // Bold usernames
                                if (part.startsWith('@')) {
                                  return <strong key={index} className="font-semibold">{part}</strong>;
                                }
                                // Italicize hashtags
                                else if (part.startsWith('#')) {
                                  return <em key={index}>{part}</em>;
                                }
                                return part;
                              });
                            };
                            
                            // Process children recursively
                            const processChildren = (children: React.ReactNode): React.ReactNode => {
                              if (Array.isArray(children)) {
                                return children.map((child, i) => {
                                  if (typeof child === 'string') {
                                    return <span key={i}>{processText(child)}</span>;
                                  }
                                  return child;
                                });
                              } else if (typeof children === 'string') {
                                return processText(children);
                              }
                              return children;
                            };
                            
                            return (
                              <p className="text-gray-700 leading-relaxed mb-4 last:mb-0">
                                {processChildren(children)}
                              </p>
                            );
                          },
                          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                          ul: ({ children }) => <ul className="list-disc list-inside space-y-2 mb-4">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal list-inside space-y-2 mb-4">{children}</ol>,
                          li: ({ children }) => <li className="text-gray-700">{children}</li>,
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                  
                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-4 ml-2">
                      <p className="text-sm font-semibold text-gray-700 mb-2">Sources from Bluesky:</p>
                      <div className="space-y-1">
                        {message.sources.map((source, idx) => {
                          // Extract username from URL if possible
                          const match = source.match(/profile\/([^/]+)\.bsky\.social/);
                          const username = match ? `@${match[1]}` : `Source ${idx + 1}`;
                          
                          return (
                            <a
                              key={idx}
                              href={source}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-2 text-sm transition-colors group"
                            >
                              <ExternalLink className="w-3 h-3 text-purple-600" />
                              <span className="text-gray-900 font-medium group-hover:text-purple-800">{username}</span>
                            </a>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
