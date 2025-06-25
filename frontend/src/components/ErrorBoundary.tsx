'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Button } from '@/components/ui/Button'
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: ErrorInfo
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    // 에러가 발생하면 state를 업데이트하여 다음 렌더링에서 폴백 UI를 표시
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // 에러 정보를 로그에 기록
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo
    })

    // 에러 리포팅 (필요시 Sentry 등으로 전송)
    if (typeof window !== 'undefined') {
      const errorReport = {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      }
      
      try {
        localStorage.setItem('react_error_boundary', JSON.stringify(errorReport))
      } catch (e) {
        console.warn('에러 정보 저장 실패:', e)
      }
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  handleReload = () => {
    window.location.reload()
  }

  handleGoHome = () => {
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      // 커스텀 폴백 UI가 제공된 경우 사용
      if (this.props.fallback) {
        return this.props.fallback
      }

      // 기본 에러 UI
      return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center p-4">
          <div className="max-w-lg w-full bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                앱에서 오류가 발생했습니다
              </h1>
              <p className="text-gray-600">
                React 컴포넌트에서 예상치 못한 오류가 발생했습니다.
              </p>
            </div>

            {/* 에러 세부사항 (개발 모드에서만) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mb-6 p-4 bg-red-50 rounded-lg">
                <div className="flex items-center mb-2">
                  <Bug className="w-4 h-4 text-red-600 mr-2" />
                  <h3 className="text-sm font-semibold text-red-800">개발자 정보:</h3>
                </div>
                <div className="text-xs text-red-700 space-y-2">
                  <div>
                    <strong>에러:</strong> {this.state.error.message}
                  </div>
                  {this.state.error.stack && (
                    <details className="mt-2">
                      <summary className="cursor-pointer font-medium">스택 트레이스</summary>
                      <pre className="mt-1 text-xs bg-red-100 p-2 rounded overflow-auto max-h-32">
                        {this.state.error.stack}
                      </pre>
                    </details>
                  )}
                  {this.state.errorInfo?.componentStack && (
                    <details className="mt-2">
                      <summary className="cursor-pointer font-medium">컴포넌트 스택</summary>
                      <pre className="mt-1 text-xs bg-red-100 p-2 rounded overflow-auto max-h-32">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            )}

            {/* 액션 버튼들 */}
            <div className="space-y-3">
              <Button
                onClick={this.handleReset}
                className="w-full flex items-center justify-center"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                컴포넌트 다시 로드
              </Button>
              
              <Button
                onClick={this.handleReload}
                variant="outline"
                className="w-full flex items-center justify-center"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                페이지 새로고침
              </Button>
              
              <Button
                onClick={this.handleGoHome}
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
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• 브라우저 캐시와 쿠키를 지워보세요</li>
                <li>• 브라우저를 최신 버전으로 업데이트해보세요</li>
                <li>• 다른 브라우저에서 시도해보세요</li>
                <li>• 브라우저 개발자 도구에서 콘솔 에러를 확인해보세요</li>
              </ul>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary 