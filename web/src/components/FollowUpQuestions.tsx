'use client';

import { ArrowRight, MessageSquare } from 'lucide-react';

interface FollowUpQuestionsProps {
  questions: string[];
  onQuestionClick: (question: string) => void;
}

export default function FollowUpQuestions({ 
  questions, 
  onQuestionClick 
}: FollowUpQuestionsProps) {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="w-full max-w-3xl mx-auto mt-6 animate-slide-up">
      <div className="glass-morphism rounded-2xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <MessageSquare className="w-5 h-5 text-purple-600" />
          <h3 className="font-semibold text-gray-800">Follow-up Questions</h3>
        </div>
        <div className="grid gap-3">
          {questions.map((question, idx) => (
            <button
              key={idx}
              onClick={() => onQuestionClick(question)}
              className="group flex items-center justify-between p-3 rounded-xl bg-white/50 hover:bg-white/80 border border-gray-200 hover:border-purple-300 transition-all duration-200 text-left"
            >
              <span className="text-sm text-gray-700 group-hover:text-gray-900">
                {question}
              </span>
              <ArrowRight className="w-4 h-4 text-purple-500 opacity-0 group-hover:opacity-100 transform translate-x-0 group-hover:translate-x-1 transition-all duration-200" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}