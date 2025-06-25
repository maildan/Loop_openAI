import { NextRequest, NextResponse } from 'next/server'

// Next.js API Route 응답 크기 제한 해제 (긴 소설 생성을 위해)
export const config = {
  api: {
    responseLimit: '10mb', // 10MB로 제한 증가
  },
}

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface ChatRequest {
  message: string
  history?: Message[]
  model?: string
  maxTokens?: number
  isLongForm?: boolean // 긴 텍스트 생성 모드
  continueStory?: boolean // 이야기 계속하기 모드
}

interface ChatResponse {
  response: string
  model: string
  tokens: number
  cost: number
  isComplete?: boolean // 응답이 완료되었는지 여부
  continuationToken?: string // 계속하기를 위한 토큰
}

export async function POST(request: NextRequest) {
  try {
    // 요청 데이터 안전하게 파싱
    const requestData: ChatRequest = await request.json()
    
    if (!requestData.message || typeof requestData.message !== 'string') {
      return NextResponse.json(
        { error: '메시지가 필요합니다.' },
        { status: 400 }
      )
    }

    console.log('📤 Frontend → Backend 요청:', {
      message: requestData.message,
      historyLength: requestData.history?.length || 0
    })

    // 백엔드 서버 연결 체크 - 실제 실행 포트로 수정
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8080'
    
    // 연결 타임아웃 설정
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 30000) // 30초 타임아웃

    try {
      const response = await fetch(`${backendUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: requestData.message,
          history: requestData.history || [],
          model: requestData.model || 'gpt-4o-mini',
          maxTokens: requestData.maxTokens || 4000, // 기본 4000 토큰
          isLongForm: requestData.isLongForm || false,
          continueStory: requestData.continueStory || false
        }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ Backend API 오류:', response.status, errorText)
        
        return NextResponse.json(
          { 
            error: `백엔드 서버 오류 (${response.status})`,
            details: errorText
          },
          { status: response.status }
        )
      }

      const data: ChatResponse = await response.json()
      
      console.log('📥 Backend → Frontend 응답:', {
        responseLength: data.response?.length || 0,
        model: data.model,
        cost: data.cost
      })

      // 응답 데이터 검증
      if (!data.response) {
        return NextResponse.json(
          { error: '백엔드에서 빈 응답을 받았습니다.' },
          { status: 500 }
        )
      }

      return NextResponse.json({
        response: data.response,
        model: data.model || 'unknown',
        tokens: data.tokens || 0,
        cost: data.cost || 0,
        isComplete: data.isComplete !== false, // 기본값은 true
        continuationToken: data.continuationToken || null
      })

    } catch (fetchError) {
      clearTimeout(timeoutId)
      
      if (fetchError instanceof Error && fetchError.name === 'AbortError') {
        console.error('⏰ 백엔드 연결 타임아웃')
        return NextResponse.json(
          { error: '백엔드 서버 응답 시간 초과' },
          { status: 504 }
        )
      }
      
      console.error('🔌 백엔드 연결 실패:', fetchError)
      return NextResponse.json(
        { 
          error: '백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.',
          details: fetchError instanceof Error ? fetchError.message : 'Connection failed'
        },
        { status: 503 }
      )
    }

  } catch (error) {
    console.error('💥 Chat API 전체 오류:', error)
    
    return NextResponse.json(
      { 
        error: '예상치 못한 오류가 발생했습니다.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
} 