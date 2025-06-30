import React, { useRef, useEffect } from 'react';
import { Send, BookOpen, FileText } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";

interface ChatInputProps {
  inputMessage: string;
  setInputMessage: (value: string) => void;
  docId: string;
  setDocId: (value: string) => void;
  isLoading: boolean;
  onSendMessage: () => void;
  onGenerateFromDocs: () => void;
  onExportToDocs: () => void;
  isMessagesEmpty: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  inputMessage,
  setInputMessage,
  docId,
  setDocId,
  isLoading,
  onSendMessage,
  onGenerateFromDocs,
  onExportToDocs,
  isMessagesEmpty,
}) => {
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      const scrollHeight = inputRef.current.scrollHeight;
      inputRef.current.style.height = `${Math.min(scrollHeight, 120)}px`;
    }
  }, [inputMessage]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (inputMessage.trim()) {
        onSendMessage();
      }
    }
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMessage.trim()) {
      onSendMessage();
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4 shrink-0 z-10">
      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleSubmit}>
          <div className="relative">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="이야기 아이디어를 입력하세요..."
              className="w-full h-12 pr-12 pl-4 py-3 rounded-full bg-gray-100 dark:bg-gray-700 border border-transparent focus:ring-2 focus:ring-purple-500 focus:outline-none resize-none transition-all duration-200"
              rows={1}
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button type="submit" size="icon" className="w-9 h-9 rounded-full" disabled={isLoading || !inputMessage.trim()}>
                    <Send className="w-5 h-5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>보내기</TooltipContent>
              </Tooltip>
            </div>
          </div>
        </form>
        <div className="mt-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={docId}
              onChange={(e) => setDocId(e.target.value)}
              placeholder="Google Docs ID 붙여넣기"
              className="text-sm px-3 py-1.5 rounded-md bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 focus:ring-1 focus:ring-purple-500 focus:outline-none w-48"
            />
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="sm" onClick={onGenerateFromDocs} disabled={!docId.trim() || isLoading}>
                  <BookOpen className="w-4 h-4 mr-2" />
                  Docs로 생성
                </Button>
              </TooltipTrigger>
              <TooltipContent>Google Docs 내용으로 스토리 생성</TooltipContent>
            </Tooltip>
          </div>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="sm" onClick={onExportToDocs} disabled={isMessagesEmpty || isLoading}>
                <FileText className="w-4 h-4 mr-2" />
                대화 내용 저장
              </Button>
            </TooltipTrigger>
            <TooltipContent>대화 내용을 Google Docs로 내보내기</TooltipContent>
          </Tooltip>
        </div>
      </div>
    </div>
  );
};

export default ChatInput; 