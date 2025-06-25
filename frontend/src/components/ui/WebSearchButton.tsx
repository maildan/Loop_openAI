"use client";

import { useState, useRef, useEffect, FC, FormEvent } from "react";
import { Search, Send, Sparkles, Loader2, X, Globe, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

interface WebSearchButtonProps {
  onSearch: (query: string) => void;
  className?: string;
  placeholder?: string;
  loading?: boolean;
}

const WebSearchButton: FC<WebSearchButtonProps> = ({ 
  onSearch, 
  className = "", 
  placeholder = "무엇이든 물어보세요...",
  loading = false
}) => {
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSearch(query.trim());
      // 검색 후에도 입력값 유지
      // setQuery("");
    }
  };

  // 텍스트 영역 높이 자동 조절
  const adjustTextareaHeight = () => {
    const textarea = inputRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  };

  // Enter 키 처리
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    adjustTextareaHeight();
  }, [query]);

  // 입력창 초기화
  const clearInput = () => {
    setQuery("");
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  return (
    <div className="flex flex-col w-full max-w-3xl mx-auto">
      <form
        onSubmit={handleSubmit}
        className={cn(
          "relative w-full rounded-xl transition-all duration-300",
          isFocused 
            ? "ring-2 ring-blue-500/50 dark:ring-blue-400/50 shadow-lg shadow-blue-500/10 dark:shadow-blue-400/5" 
            : "ring-1 ring-gray-200 dark:ring-gray-700 shadow-md",
          loading ? "bg-gray-50 dark:bg-gray-800/50" : "bg-white dark:bg-gray-800",
          className
        )}
      >
        <div className="flex items-center w-full p-3">
          <div className="flex-shrink-0 mx-2">
            {loading ? (
              <Loader2 className="w-5 h-5 text-blue-500 dark:text-blue-400 animate-spin" />
            ) : (
              <div className="relative">
                <Globe className="w-5 h-5 text-blue-500 dark:text-blue-400" />
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              </div>
            )}
          </div>
          <textarea
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyPress}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            disabled={loading}
            className="flex-grow bg-transparent text-gray-800 dark:text-gray-100 placeholder-gray-400 focus:outline-none px-2 py-2 resize-none overflow-hidden min-h-[40px] max-h-[200px] disabled:opacity-60"
            rows={1}
          />
          
          {query.length > 0 && !loading && (
            <button
              type="button"
              onClick={clearInput}
              className="flex-shrink-0 p-1.5 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 rounded-full transition-colors"
              aria-label="Clear input"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          
          <button
            type="submit"
            className={cn(
              "flex-shrink-0 p-2 rounded-lg transition-all duration-200 mx-1 flex items-center justify-center",
              query.trim() && !loading
                ? "text-white bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 shadow-md shadow-blue-500/20"
                : "bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-700 dark:text-gray-500"
            )}
            disabled={!query.trim() || loading}
            aria-label="Search"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
      
      <div className="flex items-center justify-center mt-2 text-xs text-gray-500 dark:text-gray-400 space-x-1">
        <Zap className="w-3 h-3" />
        <span>Loop AI - 기가차드급 창작 어시스턴트</span>
      </div>
    </div>
  );
};

export default WebSearchButton;