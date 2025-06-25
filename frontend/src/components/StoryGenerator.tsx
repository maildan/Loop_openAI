'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import MarkdownRenderer from '@/components/MarkdownRenderer'
import { 
  Send, 
  Bot, 
  User, 
  Search, 
  FileText, 
  Settings, 
  Sparkles,
  Copy,
  Download,
  ExternalLink,
  Loader2,
  MessageCircle,
  Globe,
  BookOpen,
  Palette,
  Zap
} from 'lucide-react'

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
  const [isLongFormMode, setIsLongFormMode] = useState(false) // 긴 소설 모드
  const [maxTokens, setMaxTokens] = useState(4000) // 최대 토큰 수
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // 자동 스크롤
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // 입력창 자동 크기 조절
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`
    }
  }, [inputMessage])

  // 서버 상태 확인
  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 5000) // 5초 타임아웃

        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: 'health_check', history: [] }),
          signal: controller.signal
        })
        
        clearTimeout(timeoutId)
        setServerStatus(response.ok ? 'online' : 'offline')
      } catch (error) {
        console.log('서버 상태 확인 실패:', error instanceof Error ? error.message : 'Unknown error')
        setServerStatus('offline')
      }
    }

    // 초기 상태 확인
    checkServerStatus()
    
    // 주기적 상태 확인 (30초마다)
    const interval = setInterval(checkServerStatus, 30000)
    
    // 페이지 포커스 시 상태 확인
    const handleFocus = () => {
      if (document.visibilityState === 'visible') {
        checkServerStatus()
      }
    }
    
    document.addEventListener('visibilitychange', handleFocus)
    window.addEventListener('focus', checkServerStatus)
    
    return () => {
      clearInterval(interval)
      document.removeEventListener('visibilitychange', handleFocus)
      window.removeEventListener('focus', checkServerStatus)
    }
  }, [])

  const sendMessage = async (content: string, continueStory: boolean = false) => {
    if (!content.trim() || isLoading) return

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: content.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    let retryCount = 0
    const maxRetries = 3

    const attemptSend = async (): Promise<void> => {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 30000) // 30초 타임아웃

        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
                  body: JSON.stringify({
          message: userMessage.content,
          history: messages.slice(-10),
          model: 'gpt-4o-mini',
          maxTokens: maxTokens,
          isLongForm: isLongFormMode,
          continueStory: continueStory
        }),
          signal: controller.signal
        })

        clearTimeout(timeoutId)

        if (!response.ok) {
          const errorText = await response.text()
          let errorData
          try {
            errorData = JSON.parse(errorText)
          } catch {
            errorData = { error: errorText || `HTTP ${response.status}` }
          }
          throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()

        if (!data.response) {
          throw new Error('서버에서 빈 응답을 받았습니다.')
        }

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
        console.error(`메시지 전송 시도 ${retryCount + 1}/${maxRetries} 실패:`, error)
        
        // AbortError (타임아웃)인 경우
        if (error instanceof Error && error.name === 'AbortError') {
          if (retryCount < maxRetries - 1) {
            retryCount++
            console.log(`타임아웃으로 인한 재시도 ${retryCount}/${maxRetries}`)
            await new Promise(resolve => setTimeout(resolve, 1000 * retryCount)) // 점진적 백오프
            return attemptSend()
          } else {
            throw new Error('요청 시간이 초과되었습니다. 네트워크 연결을 확인해주세요.')
          }
        }

        // 네트워크 오류인 경우 재시도
        if (error instanceof TypeError && error.message.includes('fetch')) {
          if (retryCount < maxRetries - 1) {
            retryCount++
            console.log(`네트워크 오류로 인한 재시도 ${retryCount}/${maxRetries}`)
            await new Promise(resolve => setTimeout(resolve, 1000 * retryCount))
            return attemptSend()
          }
        }

        // 서버 오류 (5xx)인 경우 재시도
        if (error instanceof Error && error.message.includes('HTTP 5')) {
          if (retryCount < maxRetries - 1) {
            retryCount++
            console.log(`서버 오류로 인한 재시도 ${retryCount}/${maxRetries}`)
            await new Promise(resolve => setTimeout(resolve, 2000 * retryCount))
            return attemptSend()
          }
        }

        throw error
      }
    }

    try {
      await attemptSend()
    } catch (error) {
      console.error('최종 메시지 전송 오류:', error)
      setServerStatus('offline')
      
      let errorContent = `🔌 **연결 오류**: 메시지 전송에 실패했습니다.

**오류 내용:** ${error instanceof Error ? error.message : '알 수 없는 오류'}

**해결 방법:**
1. 네트워크 연결을 확인해주세요
2. 백엔드 서버가 실행 중인지 확인해주세요 (포트 8080)
3. 브라우저를 새로고침해보세요
4. 잠시 후 다시 시도해보세요

**개발자용:** \`python src/inference/api/server.py\` 명령으로 서버를 시작하세요.`

      // 특정 오류에 대한 맞춤형 메시지
      if (error instanceof Error) {
        if (error.message.includes('타임아웃') || error.message.includes('timeout')) {
          errorContent = `⏱️ **요청 시간 초과**: 서버 응답이 너무 오래 걸립니다.

**해결 방법:**
1. 네트워크 연결 상태를 확인해주세요
2. 더 간단한 질문으로 다시 시도해보세요
3. 잠시 후 다시 시도해주세요`
        } else if (error.message.includes('HTTP 429')) {
          errorContent = `🚫 **요청 한도 초과**: 너무 많은 요청을 보냈습니다.

**해결 방법:**
1. 잠시 기다린 후 다시 시도해주세요
2. 요청 빈도를 줄여주세요`
        } else if (error.message.includes('HTTP 401') || error.message.includes('Unauthorized')) {
          errorContent = `🔐 **인증 오류**: API 키 또는 인증 정보에 문제가 있습니다.

**해결 방법:**
1. 관리자에게 문의해주세요
2. 페이지를 새로고침해보세요`
        }
      }
      
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputMessage.trim()) {
      sendMessage(inputMessage)
      setInputMessage('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleWebSearch = (query: string) => {
    const searchQuery = query.trim() || '최신 AI 뉴스'
    sendMessage(`웹에서 "${searchQuery}"에 대해 검색해서 알려주세요.`)
  }

  const continueLastStory = () => {
    const lastAssistantMessage = messages.filter(m => m.type === 'assistant').pop()
    if (lastAssistantMessage && !lastAssistantMessage.isComplete) {
      sendMessage('이야기를 계속 써주세요.', true)
    }
  }

  const exportToGoogleDocs = async () => {
    if (messages.length === 0) {
      alert('내보낼 대화 내용이 없습니다.')
      return
    }
    
    try {
      const content = messages.map(msg => 
        `${msg.type === 'user' ? '🙋‍♂️ 사용자' : '🤖 Loop AI'}\n${'-'.repeat(50)}\n${msg.content}\n\n`
      ).join('')
      
      const title = `Loop AI 대화 기록 - ${new Date().toLocaleString('ko-KR')}`
      
      const response = await fetch('/api/docs/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, content }),
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Google Docs 내보내기 실패')
      }
      
      const result = await response.json()
      
      const successMessage: Message = {
        id: `success-${Date.now()}`,
        type: 'assistant',
        content: `✅ **Google Docs 내보내기 성공!**

📄 **문서 제목**: ${result.title}
🔗 **문서 링크**: [Google Docs에서 열기](${result.url})

문서가 성공적으로 생성되었습니다. 링크를 클릭하여 확인해보세요!`,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, successMessage])
      if (result.url) {
        window.open(result.url, '_blank')
      }
    } catch (err) {
      console.error('Google Docs 내보내기 오류:', err)
      
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: `❌ **Google Docs 내보내기 실패**

**오류 내용**: ${err instanceof Error ? err.message : '알 수 없는 오류'}

**해결 방법**:
1. Google API 설정을 확인해주세요
2. 환경 변수가 올바르게 설정되었는지 확인해주세요
3. 잠시 후 다시 시도해보세요`,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, errorMessage])
    }
  }

  const generateFromGoogleDocs = async () => {
    if (!docId.trim()) {
      alert('문서 ID를 입력해주세요.')
      return
    }
    
    try {
      const response = await fetch('/api/docs/read', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ documentId: docId }),
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Google Docs 읽기 실패')
      }
      
      const result = await response.json()
      
      const prompt = `다음 Google Docs 문서 내용을 기반으로 새로운 창작물을 만들어주세요:

**문서 제목**: ${result.title}
**문서 링크**: ${result.url}

**문서 내용**:
${result.content}

위 내용을 참고하여 창의적이고 흥미로운 이야기를 만들어주세요.`

      sendMessage(prompt)
      setDocId('')
      
    } catch (err) {
      console.error('Google Docs 읽기 오류:', err)
      
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: `❌ **Google Docs 읽기 실패**

**문서 ID**: ${docId}
**오류 내용**: ${err instanceof Error ? err.message : '알 수 없는 오류'}

**해결 방법**:
1. 문서 ID가 올바른지 확인해주세요
2. 문서가 공개되어 있거나 접근 권한이 있는지 확인해주세요
3. Google API 설정을 확인해주세요`,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, errorMessage])
      setDocId('')
    }
  }

  const copyToClipboard = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content)
    } catch (err) {
      console.error('클립보드 복사 실패:', err)
    }
  }

  const recommendedPrompts = [
    '판타지 소설의 시놉시스를 작성해주세요',
    '로맨스 소설의 매력적인 캐릭터를 설정해주세요',
    'SF 단편소설의 독창적인 아이디어를 제안해주세요',
    '미스터리 소설의 반전 있는 줄거리를 만들어주세요'
  ]

  return (
    <div className={`flex flex-col h-screen bg-gray-50 ${className}`}>
      {/* 헤더 */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Loop AI</h1>
            <p className="text-sm text-gray-500">창작 전문 AI 어시스턴트</p>
          </div>
            </div>
            
        <div className="flex items-center space-x-2">
          {/* 서버 상태 */}
          <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-full ${
            serverStatus === 'online' ? 'bg-green-50' :
            serverStatus === 'offline' ? 'bg-red-50' : 'bg-yellow-50'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              serverStatus === 'online' ? 'bg-green-500' :
              serverStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'
            }`} />
            <span className={`text-sm font-medium ${
              serverStatus === 'online' ? 'text-green-700' :
              serverStatus === 'offline' ? 'text-red-700' : 'text-yellow-700'
            }`}>
              {serverStatus === 'online' ? '온라인' :
               serverStatus === 'offline' ? '오프라인' : '확인 중'}
            </span>
            </div>
            
          <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 bg-blue-50 rounded-full">
            <Zap className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-700">
              ${totalCost.toFixed(4)}
            </span>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowSettings(!showSettings)}
            className="p-2"
          >
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* 메인 채팅 영역 */}
      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* 사이드바 (설정) */}
        {showSettings && (
          <div className="w-80 bg-white border-r border-gray-200 p-4 overflow-y-auto shrink-0">
            <h3 className="font-semibold text-gray-900 mb-4">설정</h3>
            
            {/* 긴 소설 설정 */}
            <Card className="p-4 mb-4">
              <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                <BookOpen className="w-4 h-4 mr-2 text-purple-500" />
                소설 생성 설정
              </h4>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">
                    긴 소설 모드
                  </label>
                  <button
                    onClick={() => setIsLongFormMode(!isLongFormMode)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      isLongFormMode ? 'bg-purple-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        isLongFormMode ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    최대 토큰 수: {maxTokens.toLocaleString()}
                  </label>
                  <input
                    type="range"
                    min="1000"
                    max="8000"
                    step="500"
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>1K (짧게)</span>
                    <span>4K (보통)</span>
                    <span>8K (길게)</span>
                  </div>
                </div>
                
                <div className="text-xs text-gray-500">
                  <p>💡 <strong>긴 소설 모드:</strong> 더 풍부한 묘사와 세부사항</p>
                  <p>🔢 <strong>토큰 수:</strong> 높을수록 더 긴 텍스트, 더 많은 비용</p>
                </div>
              </div>
            </Card>

            {/* Google Docs 연동 */}
            <Card className="p-4 mb-4">
              <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                <FileText className="w-4 h-4 mr-2 text-blue-500" />
                Google Docs 연동
              </h4>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    문서 ID
                  </label>
                  <input
                    type="text"
                    value={docId}
                    onChange={(e) => setDocId(e.target.value)}
                    placeholder="Google Docs 문서 ID 입력"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-500 bg-white"
                  />
                </div>
                
                <div className="flex space-x-2">
                  <Button
                    onClick={generateFromGoogleDocs}
                    disabled={!docId.trim()}
                    size="sm"
                    className="flex-1"
                  >
                    <BookOpen className="w-4 h-4 mr-2" />
                    이야기 생성
                  </Button>
                  
                  <Button
                    onClick={exportToGoogleDocs}
                    disabled={messages.length === 0}
                    variant="outline"
                    size="sm"
                    className="flex-1"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    내보내기
                  </Button>
                </div>
              </div>
            </Card>

            {/* 추천 프롬프트 */}
            <Card className="p-4">
              <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                <Palette className="w-4 h-4 mr-2 text-purple-500" />
                추천 프롬프트
              </h4>
              
              <div className="space-y-2">
                {recommendedPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setInputMessage(prompt)
                      if (inputRef.current) {
                        inputRef.current.focus()
                      }
                    }}
                    className="w-full text-left p-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </Card>
          </div>
        )}
        
        {/* 채팅 영역 */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* 메시지 목록 */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
                  <MessageCircle className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Loop AI와 함께 창작해보세요!
              </h3>
                <p className="text-gray-600 mb-6 max-w-md">
                  소설, 시나리오, 캐릭터 설정 등 창작 활동을 도와드립니다.
                  아래 입력창에 질문을 입력해보세요.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-lg">
                <Button
                  variant="outline"
                    onClick={() => setInputMessage('판타지 소설의 시놉시스를 작성해주세요')}
                    className="justify-start"
                >
                    <BookOpen className="w-4 h-4 mr-2" />
                    판타지 시놉시스
                </Button>
                <Button
                  variant="outline"
                    onClick={() => setInputMessage('로맨스 소설의 매력적인 캐릭터를 설정해주세요')}
                    className="justify-start"
                  >
                    <User className="w-4 h-4 mr-2" />
                    캐릭터 설정
                  </Button>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-2xl ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                    {/* 아바타와 메타데이터 */}
                    <div className={`flex items-center mb-2 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`flex items-center space-x-2 ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          message.type === 'user' 
                            ? 'bg-blue-500' 
                            : 'bg-gradient-to-r from-purple-500 to-pink-500'
                        }`}>
                          {message.type === 'user' ? (
                            <User className="w-4 h-4 text-white" />
                          ) : (
                            <Bot className="w-4 h-4 text-white" />
                          )}
                        </div>
                        <div className={`text-xs text-gray-500 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                          <div>{message.type === 'user' ? '사용자' : 'Loop AI'}</div>
                          <div>{message.timestamp.toLocaleTimeString()}</div>
                        </div>
                      </div>
                    </div>

                    {/* 메시지 버블 */}
                    <div className={`relative p-4 rounded-2xl shadow-sm ${
                      message.type === 'user'
                        ? 'bg-blue-500 text-white rounded-tr-none'
                        : 'bg-white text-gray-900 rounded-tl-none border border-gray-200'
                    }`}>
                      {message.type === 'user' ? (
                        <div className="whitespace-pre-wrap break-words">
                          {message.content}
                        </div>
                      ) : (
                        <MarkdownRenderer 
                          content={message.content} 
                          className="text-gray-900"
                        />
                      )}
                      
                      {/* 메시지 액션 */}
                      <div className={`flex items-center justify-between mt-3 pt-3 border-t ${
                        message.type === 'user' 
                          ? 'border-blue-400' 
                          : 'border-gray-100'
                      }`}>
                        <div className="flex items-center space-x-2">
                          {message.model && (
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              message.type === 'user'
                                ? 'bg-blue-400 text-blue-100'
                                : 'bg-gray-100 text-gray-600'
                            }`}>
                              {message.model}
                            </span>
                          )}
                          {message.cost && (
                            <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">
                              ${message.cost.toFixed(6)}
                            </span>
                          )}
                        </div>
                        
                                                <div className="flex items-center space-x-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(message.content)}
                            className={`p-1 ${
                              message.type === 'user'
                                ? 'text-blue-100 hover:text-white hover:bg-blue-400'
                                : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                            }`}
                          >
                            <Copy className="w-3 h-3" />
                          </Button>
                          
                          {/* 계속하기 버튼 (AI 메시지이고 미완성인 경우) */}
                          {message.type === 'assistant' && message.isComplete === false && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => sendMessage('이야기를 계속 써주세요.', true)}
                              className="p-1 text-green-500 hover:text-green-600 hover:bg-green-50"
                              title="이야기 계속하기"
                            >
                              <MessageCircle className="w-3 h-3" />
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
            
            {/* 로딩 인디케이터 */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-2xl">
                  <div className="flex items-center mb-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center mr-2">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="text-xs text-gray-500">
                      <div>Loop AI</div>
                      <div>
                        {serverStatus === 'offline' ? '연결 중...' : '생각 중...'}
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-2xl rounded-tl-none border border-gray-200 p-4">
                    <div className="flex items-center space-x-2">
                      <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                      <span className="text-sm text-gray-500">
                        {serverStatus === 'offline' ? '서버에 연결 중...' : 'AI가 답변을 생성하고 있습니다...'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* 입력 영역 */}
          <div className="border-t border-gray-200 bg-white p-4 shrink-0">
            {/* 액션 버튼들 */}
            <div className="flex items-center space-x-2 mb-3 flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleWebSearch(inputMessage || '최신 AI 뉴스')}
                disabled={isLoading || serverStatus === 'offline'}
                className="flex items-center"
              >
                <Globe className="w-4 h-4 mr-2" />
                웹 검색
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSettings(!showSettings)}
                className="flex items-center"
              >
                <Settings className="w-4 h-4 mr-2" />
                설정
              </Button>

              {/* 긴 소설 모드 표시 */}
              {isLongFormMode && (
                <div className="flex items-center px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs">
                  <BookOpen className="w-3 h-3 mr-1" />
                  긴 소설 모드
                </div>
              )}

              {/* 토큰 수 표시 */}
              <div className="flex items-center px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                <Zap className="w-3 h-3 mr-1" />
                {maxTokens.toLocaleString()} 토큰
              </div>
            </div>

            {/* 입력 폼 */}
            <form onSubmit={handleSubmit} className="flex items-end space-x-3">
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="메시지를 입력하세요... (Shift+Enter로 줄바꿈)"
                  className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 bg-white"
                  rows={1}
                  style={{ minHeight: '48px', maxHeight: '120px' }}
                  disabled={isLoading || serverStatus === 'offline'}
                />
            </div>
              
              <Button
                type="submit"
                disabled={!inputMessage.trim() || isLoading || serverStatus === 'offline'}
                className="w-12 h-12 rounded-xl flex items-center justify-center"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StoryGenerator 