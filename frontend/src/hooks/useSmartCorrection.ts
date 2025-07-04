'use client'

import { useState, useEffect, useRef, useCallback } from 'react'

interface CorrectionResult {
  original_text: string
  corrected_text: string
  reason: string | null
  context_analysis: string | null
}

export function useSmartCorrection(
  text: string,
  fullDocument: string,
  delay: number = 1500
) {
  const [correction, setCorrection] = useState<CorrectionResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null)
  const lastCheckedText = useRef<string>('')

  const shouldCheck = useCallback((currentText: string) => {
    // 최소 길이 체크
    if (currentText.length < 5) return false
    // 마지막으로 체크한 텍스트와 동일하면 중복 체크 방지
    if (currentText === lastCheckedText.current) return false
    return true
  }, [])

  const fetchCorrection = useCallback(async () => {
    if (!shouldCheck(text)) {
      setCorrection(null)
      return
    }

    setIsLoading(true)
    lastCheckedText.current = text // API 호출 직전에 마지막 텍스트 기록

    try {
      const response = await fetch('/api/spellcheck', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          full_document: fullDocument,
          use_ai: true,
        }),
      })

      if (!response.ok) {
        // 오류 응답 처리
        setCorrection(null)
        return
      }

      const data: CorrectionResult = await response.json()
      
      // 교정 전/후 텍스트가 동일하면 제안하지 않음
      if (data.original_text === data.corrected_text) {
        setCorrection(null)
      } else {
        setCorrection(data)
      }

    } catch (error) {
      setCorrection(null)
    } finally {
      setIsLoading(false)
    }
  }, [text, fullDocument, shouldCheck])

  useEffect(() => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current)
    }

    debounceTimeout.current = setTimeout(() => {
      fetchCorrection()
    }, delay)

    return () => {
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current)
      }
    }
  }, [text, delay, fetchCorrection])

  const resetCorrection = () => {
    setCorrection(null)
    lastCheckedText.current = text // 교정 적용 후, 현재 텍스트를 마지막으로 체크한 것으로 간주
  }

  return { correction, isLoading, resetCorrection }
} 