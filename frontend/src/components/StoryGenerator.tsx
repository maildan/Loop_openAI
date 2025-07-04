'use client'

import React, { useState, useEffect } from 'react'
import ChatHeader from './chat/ChatHeader'
import ChatMessageList from './chat/ChatMessageList'
import ChatInput from './chat/ChatInput'
import SettingsSidebar from './chat/SettingsSidebar'
import { useSmartCorrection } from '@/hooks/useSmartCorrection'
import CorrectionSuggestion from './chat/CorrectionSuggestion'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  model?: string
  cost?: number
  isComplete?: boolean
  continuationToken?: string
}

interface StoryGeneratorProps {
  className?: string
}

const StoryGenerator: React.FC<StoryGeneratorProps> = ({ className = '' }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [docId, setDocId] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [totalCost, setTotalCost] = useState(0)
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [isLongFormMode, setIsLongFormMode] = useState(false)
  const [maxTokens, setMaxTokens] = useState(4000)

  // AI 스마트 교정 Hook
  const fullDocumentForCorrection = messages.map(m => m.content).join('\n')
  const { 
    correction, 
    isLoading: isCorrectionLoading, 
    resetCorrection 
  } = useSmartCorrection(inputMessage, fullDocumentForCorrection)

  // 서버 상태 확인
  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 5000)

        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: 'health_check', history: [] }),
          signal: controller.signal
        })
        
        clearTimeout(timeoutId)
        setServerStatus(response.ok ? 'online' : 'offline')
      } catch (error) {
        setServerStatus('offline')
      }
    }
    checkServerStatus()
    const interval = setInterval(checkServerStatus, 30000)
    const handleFocus = () => {
      if (document.visibilityState === 'visible') checkServerStatus()
    }
    document.addEventListener('visibilitychange', handleFocus)
    window.addEventListener('focus', checkServerStatus)
    
    return () => {
      clearInterval(interval)
      document.removeEventListener('visibilitychange', handleFocus)
      window.removeEventListener('focus', checkServerStatus)
    }
  }, [])

  const handleSendMessage = async (content: string, continueStory: boolean = false) => {
    if (!content.trim() || isLoading) return

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: content.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    if (!continueStory) setInputMessage('')
    setIsLoading(true)

    try {
      // API 요청 전, 프론트엔드 상태(type)를 백엔드 모델(role)에 맞게 우아하게 변환
      const historyForAPI = messages.slice(-10).map(msg => ({
        role: msg.type,
        content: msg.content
      }));

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          history: historyForAPI, // 변환된 데이터를 사용
          model: 'gpt-4o-mini',
          maxTokens: maxTokens,
          isLongForm: isLongFormMode,
          continueStory: continueStory
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(JSON.parse(errorText).error || `HTTP ${response.status}`)
      }

      const data = await response.json()
      if (!data.response) throw new Error('서버에서 빈 응답을 받았습니다.')

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: data.response,
        timestamp: new Date(),
        model: data.model,
        cost: data.cost,
        isComplete: data.isComplete,
        continuationToken: data.continuationToken
      }

      setMessages(prev => [...prev, assistantMessage])
      if (data.cost) setTotalCost(prev => prev + data.cost)
      setServerStatus('online')

    } catch (error) {
      setServerStatus('offline')
      const errorContent = `🔌 **연결 오류**: ${error instanceof Error ? error.message : '알 수 없는 오류'}`
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: errorContent,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const continueLastStory = () => {
    const lastAssistantMessage = messages.filter(m => m.type === 'assistant').pop()
    if (lastAssistantMessage && !lastAssistantMessage.isComplete) {
      handleSendMessage('이야기를 계속 써주세요.', true)
    }
  }

  const exportToGoogleDocs = async () => {
    if (messages.length === 0) return alert('내보낼 대화 내용이 없습니다.')
    
    try {
      const content = messages.map(msg => `${msg.type === 'user' ? '🙋‍♂️ 사용자' : '🤖 Loop AI'}\n${'-'.repeat(50)}\n${msg.content}\n\n`).join('')
      const title = `Loop AI 대화 기록 - ${new Date().toLocaleString('ko-KR')}`
      
      const response = await fetch('/api/docs/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      })
      
      if (!response.ok) throw new Error((await response.json()).error || 'Google Docs 내보내기 실패')
      
      const result = await response.json()
      const successMessage: Message = {
        id: `success-${Date.now()}`,
        type: 'assistant',
        content: `✅ **Google Docs 내보내기 성공!**\n[문서 바로가기](${result.url})`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, successMessage])
      if (result.url) window.open(result.url, '_blank')

    } catch (err) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: `❌ **Google Docs 내보내기 실패**: ${err instanceof Error ? err.message : '알 수 없는 오류'}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  }

  const generateFromGoogleDocs = async () => {
    if (!docId.trim()) return alert('문서 ID를 입력해주세요.')
    
    try {
      const response = await fetch('/api/docs/read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ documentId: docId }),
      })
      
      if (!response.ok) throw new Error((await response.json()).error || 'Google Docs 읽기 실패')
      
      const result = await response.json()
      const prompt = `다음 Google Docs 문서 내용을 기반으로 새로운 창작물을 만들어주세요:\n\n**문서 내용**:\n${result.content}`
      handleSendMessage(prompt)
      setDocId('')
      
    } catch (err) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: `❌ **Google Docs 읽기 실패**: ${err instanceof Error ? err.message : '알 수 없는 오류'}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  }

  const copyToClipboard = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      const successMessage: Message = {
        id: `success-${Date.now()}`,
        type: 'assistant',
        content: `✅ **클립보드에 복사되었습니다.**`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, successMessage])
    } catch (err) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: `❌ **복사 실패**: ${err instanceof Error ? err.message : '알 수 없는 오류'}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  }

  const recommendedPrompts = [
    '흥미로운 캐릭터 설정 3가지를 제안해줘',
    '예상치 못한 반전이 있는 단편 소설의 시작 부분을 써줘',
    '일상적인 물건에 숨겨진 비밀에 대한 단편 소설 아이디어 줘'
  ]

  const handleApplyCorrection = (correctedText: string) => {
    setInputMessage(correctedText)
    resetCorrection()
  }

  const handleDismissCorrection = () => {
    resetCorrection()
  }

  return (
    <div className={`flex flex-col h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 ${className}`}>
      <ChatHeader 
        serverStatus={serverStatus}
        totalCost={totalCost}
        onToggleSettings={() => setShowSettings(!showSettings)}
      />
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col relative">
          <ChatMessageList
            messages={messages}
            isLoading={isLoading}
            recommendedPrompts={recommendedPrompts}
            onSendMessage={(prompt) => handleSendMessage(prompt)}
            onContinueStory={continueLastStory}
            onCopyToClipboard={copyToClipboard}
          />
          <div className="relative">
            {correction && !isCorrectionLoading && (
              <CorrectionSuggestion
                correction={correction}
                onApply={handleApplyCorrection}
                onDismiss={handleDismissCorrection}
                isLoading={isCorrectionLoading}
              />
            )}
            {isCorrectionLoading && (
               <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-gray-700 text-white text-sm rounded-lg px-3 py-2 shadow-lg animate-pulse">
                AI 분석 중...
              </div>
            )}
            <ChatInput
              inputMessage={inputMessage}
              setInputMessage={setInputMessage}
              docId={docId}
              setDocId={setDocId}
              isLoading={isLoading}
              onSendMessage={() => handleSendMessage(inputMessage)}
              onGenerateFromDocs={generateFromGoogleDocs}
              onExportToDocs={exportToGoogleDocs}
              isMessagesEmpty={messages.length === 0}
            />
          </div>
        </div>
        <SettingsSidebar
          showSettings={showSettings}
          isLongFormMode={isLongFormMode}
          setIsLongFormMode={setIsLongFormMode}
          maxTokens={maxTokens}
          setMaxTokens={setMaxTokens}
        />
      </div>
    </div>
  )
}

export default StoryGenerator 