import { NextRequest, NextResponse } from 'next/server'
import { Readable } from 'stream'

// Next.js API Route 응답 크기 제한 해제 (긴 소설 생성을 위해) -> App Router에서는 사용되지 않음
// export const config = {
//   api: {
//     responseLimit: '10mb', // 10MB로 제한 증가
//   },
// }

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

const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8080'

// Node.js의 ReadableStream을 Web API의 ReadableStream으로 변환하는 헬퍼 함수
async function* nodeStreamToIterator(stream: NodeJS.ReadableStream) {
  for await (const chunk of stream) {
    yield chunk
  }
}

function iteratorToStream(iterator: AsyncGenerator<any, void, unknown>) {
  return new ReadableStream({
    async pull(controller) {
      const { value, done } = await iterator.next()
      if (done) {
        controller.close()
      } else {
        controller.enqueue(value)
      }
    },
  })
}

export async function POST(request: NextRequest) {
  try {
    const requestData = await request.json()

    // 백엔드로 스트리밍 요청 전달
    const response = await fetch(`${backendUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/plain', // 스트림을 기대함을 명시
      },
      body: JSON.stringify(requestData),
    })

    // 백엔드에서 에러 응답이 온 경우
    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ Backend API 오류:', response.status, errorText)
      return new Response(errorText, {
        status: response.status,
        headers: { 'Content-Type': 'application/json' },
      })
    }
    
    // 응답 스트림을 클라이언트로 그대로 전달
    if (response.body) {
      const stream = iteratorToStream(nodeStreamToIterator(response.body as any))
      return new Response(stream, {
        status: 200,
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
        },
      })
    }

    return new Response('백엔드에서 응답이 없습니다.', { status: 500 })

  } catch (error) {
    console.error('💥 Chat API 프록시 오류:', error)
    const errorMessage = error instanceof Error ? error.message : 'Unknown proxy error'
    return new Response(JSON.stringify({ error: '프록시 서버 오류', details: errorMessage }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    })
  }
} 