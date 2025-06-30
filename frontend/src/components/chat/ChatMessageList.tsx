import React, { useRef, useEffect } from 'react';
import { Bot, User, Loader2, Sparkles, Copy } from 'lucide-react';
import MarkdownRenderer from '@/components/MarkdownRenderer';
import { Button } from '@/components/ui/Button';
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  model?: string;
  cost?: number;
  isComplete?: boolean;
  continuationToken?: string;
}

interface ChatMessageListProps {
  messages: Message[];
  isLoading: boolean;
  recommendedPrompts: string[];
  onSendMessage: (content: string) => void;
  onContinueStory: () => void;
  onCopyToClipboard: (content: string) => void;
}

const ChatMessageList: React.FC<ChatMessageListProps> = ({
  messages,
  isLoading,
  recommendedPrompts,
  onSendMessage,
  onContinueStory,
  onCopyToClipboard,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <main className="flex-1 flex flex-col overflow-y-auto">
      <div className="flex-1 p-4 space-y-6">
        {messages.length === 0 && !isLoading ? (
          <div className="text-center text-gray-500 dark:text-gray-400 pt-16">
            <Bot size={48} className="mx-auto mb-4 opacity-50" />
            <h2 className="text-2xl font-semibold mb-2">무엇을 도와드릴까요?</h2>
            <p className="mb-8">아래 프롬프트 예시를 사용하거나 직접 입력해보세요.</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
              {recommendedPrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => onSendMessage(prompt)}
                  className="bg-white dark:bg-gray-800 p-4 rounded-lg text-left hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 shadow-sm border border-gray-200 dark:border-gray-700"
                >
                  <p className="font-medium">{prompt}</p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`flex items-start gap-4 ${message.type === 'user' ? 'justify-end' : ''}`}>
              {message.type === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-indigo-600 flex items-center justify-center shrink-0">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}
              <div className={`max-w-xl w-full p-4 rounded-lg ${
                message.type === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-white dark:bg-gray-800 shadow-sm border border-gray-100 dark:border-gray-700'
              }`}>
                <MarkdownRenderer content={message.content} />
                {message.type === 'assistant' && (
                  <div className="mt-3 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <div className="flex items-center gap-2">
                      {message.model && (
                        <Tooltip>
                          <TooltipTrigger>
                            <span className="font-mono bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded">{message.model}</span>
                          </TooltipTrigger>
                          <TooltipContent>모델: {message.model}</TooltipContent>
                        </Tooltip>
                      )}
                      {message.cost !== undefined && (
                        <Tooltip>
                          <TooltipTrigger>
                            <span className="font-mono bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded">${message.cost.toFixed(4)}</span>
                          </TooltipTrigger>
                          <TooltipContent>비용</TooltipContent>
                        </Tooltip>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="ghost" size="icon" className="w-7 h-7" onClick={() => onCopyToClipboard(message.content)}>
                            <Copy className="w-4 h-4" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>복사</TooltipContent>
                      </Tooltip>
                      {!message.isComplete && message.continuationToken && (
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button variant="ghost" size="icon" className="w-7 h-7" onClick={onContinueStory}>
                              <Sparkles className="w-4 h-4 text-purple-500" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>이어쓰기</TooltipContent>
                        </Tooltip>
                      )}
                    </div>
                  </div>
                )}
              </div>
              {message.type === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center shrink-0">
                  <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                </div>
              )}
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-indigo-600 flex items-center justify-center shrink-0">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="max-w-xl w-full p-4 rounded-lg bg-white dark:bg-gray-800 shadow-sm border border-gray-100 dark:border-gray-700 flex items-center space-x-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>AI가 생각 중입니다...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </main>
  );
};

export default ChatMessageList; 