'use client'

import { useState, useCallback } from 'react'
import { baseUrl } from '@/lib/utils'

// 요청/응답 타입을 채팅에 맞게 수정
interface ChatRequest {
  message: string;
  history: { role: string; content: string }[];
}

interface StoryRequest {
  prompt: string
  genre?: string
  length?: string
  style?: string
  characterName?: string
  setting?: string
  temperature?: number
  max_new_tokens?: number
}

interface StoryResponse {
  generated_text: string
  genre: string
  prompt: string
  metadata: {
    temperature: number
    max_new_tokens: number
    model: string
  }
}

interface Genre {
  value: string
  label: string
  description: string
}

export const useStoryGeneration = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // story 상태를 단일 객체가 아닌, 생성되는 텍스트를 저장하는 문자열로 변경
  const [story, setStory] = useState<string>('')

  const generateStory = useCallback(async (request: ChatRequest) => {
    setIsLoading(true)
    setError(null)
    setStory('') // 생성 시작 시 초기화
    
    try {
      console.log('🚀 기가차드 스트리밍 API 호출:', request)
      
      // 엔드포인트를 /api/chat으로 변경
      const response = await fetch(`${baseUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      console.log('📡 응답 상태:', response.status, response.statusText)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ 에러 응답:', errorText)
        throw new Error(`서버 에러 (${response.status}): ${errorText}`)
      }

      if (!response.body) {
        throw new Error('응답에 body가 없습니다.')
      }

      // 스트리밍 응답 처리 로직
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let done = false

      while (!done) {
        const { value, done: readerDone } = await reader.read()
        done = readerDone
        const chunk = decoder.decode(value, { stream: true })
        
        // 스트리밍으로 받은 텍스트를 실시간으로 상태에 추가
        setStory((prevStory) => prevStory + chunk)
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
      console.error('🔥 기가차드 스트리밍 에러:', err)
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }, [])

  return {
    generateStory,
    isLoading,
    error,
    story,
    setError,
    // 외부에서 story를 직접 설정할 수 있는 함수 추가 (필요시)
    setStory, 
  }
}

export const useGenres = () => {
  const [genres, setGenres] = useState<Genre[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const fetchGenres = useCallback(async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${baseUrl}/api/genres`)
      if (!response.ok) throw new Error('장르 목록을 가져오는데 실패했습니다.')
      
      const data = await response.json()
      setGenres(data.genres)
    } catch (err) {
      console.error('장르 로드 실패:', err)
      // 기본값 설정
      setGenres([
        { value: 'fantasy', label: '판타지', description: '마법과 모험의 세계' },
        { value: 'romance', label: '로맨스', description: '달콤한 사랑 이야기' },
        { value: 'sf', label: 'SF', description: '미래와 과학 기술' },
        { value: 'mystery', label: '미스터리', description: '수수께끼와 추리' },
        { value: 'drama', label: '드라마', description: '현실적인 인간 관계' }
      ])
    } finally {
      setIsLoading(false)
    }
  }, [])

  return {
    genres,
    fetchGenres,
    isLoading
  }
}

export const useExamples = () => {
  const [examples, setExamples] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const fetchExamples = useCallback(async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${baseUrl}/api/examples`)
      if (!response.ok) throw new Error('예시를 가져오는데 실패했습니다.')
      
      const data = await response.json()
      setExamples(data.examples)
    } catch (err) {
      console.error('예시 로드 실패:', err)
      // 기본값 설정
      setExamples([
        { prompt: '마법사와 용의 모험 이야기를 써주세요', genre: 'fantasy' },
        { prompt: '시간 여행자가 과거로 돌아가는 SF 소설을 써주세요', genre: 'sf' },
        { prompt: '첫사랑을 다시 만난 로맨스 이야기를 써주세요', genre: 'romance' }
      ])
    } finally {
      setIsLoading(false)
    }
  }, [])

  return {
    examples,
    fetchExamples,
    isLoading
  }
} 