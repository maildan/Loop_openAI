'use client'

import { useState, useCallback } from 'react'
import { baseUrl } from '@/lib/utils'

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
  const [story, setStory] = useState<StoryResponse | null>(null)

  const generateStory = useCallback(async (request: StoryRequest) => {
    setIsLoading(true)
    setError(null)
    
    try {
      console.log('🚀 기가차드 API 호출:', request)
      
      const response = await fetch(`${baseUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      console.log('📡 응답 상태:', response.status, response.statusText)
      
      // 응답이 OK가 아니면 텍스트로 읽어서 디버깅
      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ 에러 응답:', errorText)
        throw new Error(`서버 에러 (${response.status}): ${errorText}`)
      }

      // 응답 텍스트를 먼저 확인
      const responseText = await response.text()
      console.log('📄 응답 텍스트:', responseText)
      
      // JSON 파싱 시도
      let data: StoryResponse
      try {
        data = JSON.parse(responseText)
      } catch (parseError) {
        console.error('💥 JSON 파싱 실패:', parseError)
        throw new Error(`JSON 파싱 실패: ${responseText.substring(0, 100)}...`)
      }
      
      console.log('✅ 파싱 성공:', data)
      setStory(data)
      return data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
      console.error('🔥 기가차드 에러:', err)
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  return {
    generateStory,
    isLoading,
    error,
    story,
    setError
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