import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'link' | 'danger' | 'success' | 'warning' | 'info' | 'gigachad'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  fullWidth?: boolean
  rounded?: 'default' | 'full' | 'none'
  elevation?: 'none' | 'sm' | 'md' | 'lg'
  animated?: boolean
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  leftIcon,
  rightIcon,
  className = '',
  disabled,
  fullWidth = false,
  rounded = 'default',
  elevation = 'md',
  animated = true,
  ...props
}) => {
  // 기본 클래스
  const baseClasses = 'inline-flex items-center justify-center font-medium transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500/70 disabled:pointer-events-none disabled:opacity-50'
  
  // 너비 클래스
  const widthClasses = fullWidth ? 'w-full' : '';
  
  // 둥근 모서리 클래스
  const roundedClasses = {
    'default': 'rounded-md',
    'full': 'rounded-full',
    'none': 'rounded-none'
  }
  
  // 그림자 클래스
  const elevationClasses = {
    'none': '',
    'sm': 'shadow-sm',
    'md': 'shadow-md',
    'lg': 'shadow-lg'
  }
  
  // 애니메이션 클래스
  const animationClasses = animated ? 'transform hover:scale-105 active:scale-95 transition-transform' : '';
  
  // 버튼 스타일 변형
  const variantClasses = {
    primary: `bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 
              active:from-blue-800 active:to-indigo-800 dark:from-blue-500 dark:to-indigo-500 
              dark:hover:from-blue-600 dark:hover:to-indigo-600 ${elevationClasses[elevation]}`,
              
    secondary: `bg-gray-100 text-gray-800 border border-gray-300 hover:bg-gray-200 active:bg-gray-300
                dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600 dark:hover:bg-gray-600 
                dark:active:bg-gray-500 ${elevationClasses[elevation]}`,
                
    outline: `bg-transparent border-2 border-blue-500 text-blue-600 hover:bg-blue-50 active:bg-blue-100
              dark:border-blue-400 dark:text-blue-400 dark:hover:bg-blue-900/20 dark:active:bg-blue-900/30`,
              
    ghost: `bg-transparent text-gray-700 hover:bg-gray-100 active:bg-gray-200
            dark:text-gray-300 dark:hover:bg-gray-800 dark:active:bg-gray-700`,
            
    link: `bg-transparent text-blue-600 hover:text-blue-700 active:text-blue-800 underline-offset-4 hover:underline
           dark:text-blue-400 dark:hover:text-blue-300 dark:active:text-blue-200 p-0 shadow-none`,
           
    danger: `bg-gradient-to-r from-red-500 to-rose-500 text-white hover:from-red-600 hover:to-rose-600 
             active:from-red-700 active:to-rose-700 dark:from-red-600 dark:to-rose-600 
             dark:hover:from-red-500 dark:hover:to-rose-500 ${elevationClasses[elevation]}`,
             
    success: `bg-gradient-to-r from-emerald-500 to-green-500 text-white hover:from-emerald-600 hover:to-green-600 
              active:from-emerald-700 active:to-green-700 dark:from-emerald-600 dark:to-green-600 
              dark:hover:from-emerald-500 dark:hover:to-green-500 ${elevationClasses[elevation]}`,
              
    warning: `bg-gradient-to-r from-amber-500 to-yellow-500 text-white hover:from-amber-600 hover:to-yellow-600 
              active:from-amber-700 active:to-yellow-700 dark:from-amber-600 dark:to-yellow-600 
              dark:hover:from-amber-500 dark:hover:to-yellow-500 ${elevationClasses[elevation]}`,
              
    info: `bg-gradient-to-r from-cyan-500 to-sky-500 text-white hover:from-cyan-600 hover:to-sky-600 
           active:from-cyan-700 active:to-sky-700 dark:from-cyan-600 dark:to-sky-600 
           dark:hover:from-cyan-500 dark:hover:to-sky-500 ${elevationClasses[elevation]}`,
           
    gigachad: `relative overflow-hidden
      bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 
      dark:from-red-600 dark:via-orange-600 dark:to-yellow-600
      text-white font-black 
      hover:from-red-600 hover:via-orange-600 hover:to-yellow-600
      dark:hover:from-red-700 dark:hover:via-orange-700 dark:hover:to-yellow-700
      shadow-orange-500/30 hover:shadow-orange-500/50 
      dark:shadow-orange-400/40 dark:hover:shadow-orange-400/60
      transform hover:rotate-1 hover:scale-110
      border-2 border-white/30 hover:border-white/50
      before:absolute before:inset-0 before:bg-gradient-to-r 
      before:from-red-400 before:via-orange-400 before:to-yellow-400 
      before:opacity-0 hover:before:opacity-30 before:transition-opacity before:duration-300
      after:absolute after:inset-0 after:bg-gradient-to-45deg 
      after:from-transparent after:via-white/20 after:to-transparent 
      after:translate-x-[-100%] hover:after:translate-x-[100%] 
      after:transition-transform after:duration-700 after:ease-out
    `
  }
  
  // 크기 클래스
  const sizeClasses = {
    xs: 'h-7 px-2.5 text-xs',
    sm: 'h-9 px-3 py-2 text-sm',
    md: 'h-10 px-4 py-2 text-sm',
    lg: 'h-11 px-5 py-2.5 text-base',
    xl: 'h-12 px-6 py-3 text-lg'
  }

  // 모든 클래스 결합
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${roundedClasses[rounded]} ${widthClasses} ${animationClasses} ${className}`

  return (
    <button
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      
      {leftIcon && !loading && (
        <span className="mr-2 -ml-1">{leftIcon}</span>
      )}
      
      <span className="relative z-10">{children}</span>
      
      {rightIcon && (
        <span className="ml-2 -mr-1">{rightIcon}</span>
      )}
    </button>
  )
} 