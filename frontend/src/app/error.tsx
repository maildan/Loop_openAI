'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // 에러를 콘솔에 로그
    console.error('클라이언트 에러:', error)
    
    // 에러 리포팅 (필요시 Sentry 등으로 전송)
    if (typeof window !== 'undefined') {
      // 에러 정보를 localStorage에 저장
      const errorInfo = {
        message: error.message,
        stack: error.stack,
        digest: error.digest,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      }
      
      try {
        localStorage.setItem('last_error', JSON.stringify(errorInfo))
      } catch (e) {
        console.warn('에러 정보 저장 실패:', e)
      }
    }
  }, [error])

  const handleReset = () => {
    // 에러 상태 초기화
    try {
      reset()
    } catch (e) {
      console.error('리셋 실패:', e)
      // 리셋이 실패하면 페이지 새로고침
      window.location.reload()
    }
  }

  const handleReload = () => {
    window.location.reload()
  }

  const handleGoHome = () => {
    window.location.href = '/'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        <div className="mb-6">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            문제가 발생했습니다
          </h1>
          <p className="text-gray-600">
            예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해주세요.
          </p>
        </div>

        {/* 에러 세부사항 (개발 모드에서만) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mb-6 p-4 bg-red-50 rounded-lg text-left">
            <h3 className="text-sm font-semibold text-red-800 mb-2">개발자 정보:</h3>
            <p className="text-xs text-red-700 font-mono break-all">
              {error.message}
            </p>
            {error.digest && (
              <p className="text-xs text-red-600 mt-1">
                Digest: {error.digest}
              </p>
            )}
          </div>
        )}

        {/* 액션 버튼들 */}
        <div className="space-y-3">
          <Button
            onClick={handleReset}
            className="w-full flex items-center justify-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            다시 시도
          </Button>
          
          <Button
            onClick={handleReload}
            variant="outline"
            className="w-full flex items-center justify-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            페이지 새로고침
          </Button>
          
          <Button
            onClick={handleGoHome}
            variant="ghost"
            className="w-full flex items-center justify-center"
          >
            <Home className="w-4 h-4 mr-2" />
            홈으로 돌아가기
          </Button>
        </div>

        {/* 도움말 */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="text-sm font-semibold text-blue-800 mb-2">문제가 계속 발생한다면:</h3>
          <ul className="text-xs text-blue-700 space-y-1 text-left">
            <li>• 브라우저 캐시를 지워보세요</li>
            <li>• 다른 브라우저에서 시도해보세요</li>
            <li>• 네트워크 연결을 확인해보세요</li>
            <li>• 백엔드 서버가 실행 중인지 확인해보세요</li>
          </ul>
        </div>
      </div>
    </div>
  )
} 