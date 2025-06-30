import React from 'react';
import { Sparkles, Settings, Zap } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface ChatHeaderProps {
  serverStatus: 'online' | 'offline' | 'checking';
  totalCost: number;
  onToggleSettings: () => void;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({
  serverStatus,
  totalCost,
  onToggleSettings,
}) => {
  return (
    <TooltipProvider>
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between shrink-0 z-20">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Loop AI</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">창작 전문 AI 어시스턴트</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-sm font-medium ${
            serverStatus === 'online' ? 'bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300' :
            serverStatus === 'offline' ? 'bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300' :
            'bg-yellow-100 dark:bg-yellow-900/50 text-yellow-700 dark:text-yellow-400'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              serverStatus === 'online' ? 'bg-green-500' :
              serverStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'
            }`} />
            <span>{serverStatus === 'online' ? '온라인' : serverStatus === 'offline' ? '오프라인' : '확인 중'}</span>
          </div>

          <Tooltip>
            <TooltipTrigger asChild>
              <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 bg-blue-100 dark:bg-blue-900/50 rounded-full">
                <Zap className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                  ${totalCost.toFixed(4)}
                </span>
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p>누적 토큰 사용 비용</p>
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onToggleSettings} className="w-9 h-9">
                <Settings className="w-5 h-5" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>설정</p>
            </TooltipContent>
          </Tooltip>
        </div>
      </header>
    </TooltipProvider>
  );
};

export default ChatHeader; 