'use client';

export default function LoadingAnimation() {
  return (
    <div className="w-full max-w-3xl mx-auto animate-fade-in">
      <div className="glass-morphism rounded-2xl p-6">
        <div className="flex items-center gap-4">
          <div className="flex gap-2">
            <div className="w-3 h-3 bg-pink-500 rounded-full animate-pulse" style={{ animationDelay: '0ms' }} />
            <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
            <div className="w-3 h-3 bg-pink-400 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
          </div>
          <div className="flex-1">
            <p className="text-gray-600 text-sm">Searching through leftist perspectives...</p>
            <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-pink-500 to-purple-600 rounded-full animate-loading-bar" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}