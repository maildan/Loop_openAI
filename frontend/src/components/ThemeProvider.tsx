'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
  actualTheme: 'light' | 'dark'
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

interface ThemeProviderProps {
  children: React.ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>('system')
  const [actualTheme, setActualTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    // 저장된 테마 불러오기
    const savedTheme = localStorage.getItem('theme') as Theme
    if (savedTheme) {
      setTheme(savedTheme)
    }
  }, [])

  useEffect(() => {
    const root = window.document.documentElement

    const updateTheme = () => {
      let resolvedTheme: 'light' | 'dark'

      if (theme === 'system') {
        resolvedTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      } else {
        resolvedTheme = theme as 'light' | 'dark'
      }

      setActualTheme(resolvedTheme)

      // DOM에 클래스 적용
      root.classList.remove('light', 'dark')
      root.classList.add(resolvedTheme)

      // 테마 저장
      localStorage.setItem('theme', theme)
    }

    updateTheme()

    // 시스템 테마 변경 감지
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => {
      if (theme === 'system') {
        updateTheme()
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme])

  return (
    <ThemeContext.Provider value={{ theme, setTheme, actualTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

// 🔥 기가차드 테마 토글 컴포넌트
export function ThemeToggle() {
  const { theme, setTheme, actualTheme } = useTheme()

  const handleToggle = () => {
    if (theme === 'light') {
      setTheme('dark')
    } else if (theme === 'dark') {
      setTheme('system')
    } else {
      setTheme('light')
    }
  }

  const getIcon = () => {
    if (theme === 'light') return '☀️'
    if (theme === 'dark') return '🌙'
    return '🌓'
  }

  const getLabel = () => {
    if (theme === 'light') return '라이트 모드'
    if (theme === 'dark') return '다크 모드'
    return '시스템 모드'
  }

  return (
    <button
      onClick={handleToggle}
      className={`
        relative inline-flex items-center justify-center w-14 h-14 rounded-2xl
        bg-gradient-to-r from-violet-500 to-purple-600 dark:from-violet-600 dark:to-purple-700
        text-white font-bold text-xl
        hover:scale-110 active:scale-95 transition-all duration-300
        shadow-lg hover:shadow-xl hover:shadow-violet-500/30 dark:hover:shadow-violet-400/30
        border-2 border-white/20 hover:border-white/40
        ${actualTheme === 'dark' ? 'ring-2 ring-purple-400 ring-opacity-50' : ''}
      `}
      title={getLabel()}
    >
      <span className="relative z-10 drop-shadow-lg">{getIcon()}</span>
      
      {/* 기가차드 글로우 효과 */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-violet-400 to-purple-500 opacity-0 hover:opacity-20 transition-opacity duration-300 blur-xl" />
      
      {/* 펄스 애니메이션 */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-violet-500 to-purple-600 animate-pulse opacity-30" />
    </button>
  )
} 