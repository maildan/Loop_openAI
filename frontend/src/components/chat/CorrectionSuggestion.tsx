'use client'

import React from 'react'

interface CorrectionResult {
  original_text: string
  corrected_text: string
  reason: string | null
  context_analysis: string | null
}

interface CorrectionSuggestionProps {
  correction: CorrectionResult
  onApply: (correctedText: string) => void
  onDismiss: () => void
  isLoading: boolean
}

const CorrectionSuggestion: React.FC<CorrectionSuggestionProps> = ({
  correction,
  onApply,
  onDismiss,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-gray-700 text-white text-sm rounded-lg px-3 py-2 shadow-lg animate-pulse">
        AI 분석 중...
      </div>
    )
  }
  
  return (
    <div className="absolute -top-14 left-1/2 -translate-x-1/2 w-max max-w-md bg-white border border-gray-200 rounded-lg shadow-xl p-3 z-10">
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500">
          <span className="line-through">{correction.original_text}</span>
          <span className="mx-2 font-bold text-blue-600">→</span>
          <span className="font-semibold text-gray-800">{correction.corrected_text}</span>
        </p>
        <div className="flex items-center space-x-2 ml-4">
          <button
            onClick={() => onApply(correction.corrected_text)}
            className="px-3 py-1 text-sm font-semibold text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            적용
          </button>
          <button
            onClick={onDismiss}
            className="px-3 py-1 text-sm font-semibold text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none transition-colors"
          >
            무시
          </button>
        </div>
      </div>
      {correction.reason && (
        <p className="mt-2 text-xs text-gray-500 border-t pt-2">
          <span className="font-semibold">AI 제안 이유:</span> {correction.reason}
        </p>
      )}
    </div>
  )
}

export default CorrectionSuggestion 