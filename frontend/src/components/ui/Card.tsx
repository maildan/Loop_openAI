import React from 'react'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  variant?: 'default' | 'outline' | 'filled' | 'elevated' | 'glass'
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  radius?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full'
  bordered?: boolean
  hoverable?: boolean
  animated?: boolean
  customBg?: string
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  className = '', 
  variant = 'default',
  padding = 'md',
  radius = 'md',
  bordered = true,
  hoverable = true,
  animated = true,
  customBg,
  ...props 
}) => {
  // 기본 클래스
  const baseClasses = 'transition-all duration-300'
  
  // 패딩 클래스
  const paddingClasses = {
    none: 'p-0',
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-7',
    xl: 'p-9'
  }
  
  // 둥근 모서리 클래스
  const radiusClasses = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    xl: 'rounded-xl',
    full: 'rounded-3xl'
  }
  
  // 테두리 클래스
  const borderClasses = bordered 
    ? 'border border-slate-200 dark:border-slate-700'
    : ''
  
  // 호버 클래스
  const hoverClasses = hoverable 
    ? 'hover:border-blue-500/30 dark:hover:border-blue-400/30 hover:shadow-lg'
    : ''
  
  // 애니메이션 클래스
  const animationClasses = animated
    ? 'transform hover:-translate-y-1 transition-transform'
    : ''
  
  // 변형 클래스
  const variantClasses = {
    default: customBg || 'bg-white dark:bg-gray-800',
    outline: 'bg-transparent',
    filled: customBg || 'bg-gray-100 dark:bg-gray-700',
    elevated: customBg || 'bg-white dark:bg-gray-800 shadow-lg',
    glass: 'bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg'
  }
  
  const classes = `${baseClasses} ${paddingClasses[padding]} ${radiusClasses[radius]} ${borderClasses} ${hoverable ? hoverClasses : ''} ${animated ? animationClasses : ''} ${variantClasses[variant]} ${className}`
  
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  )
}

interface CardComponentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export const CardHeader: React.FC<CardComponentProps> = ({ children, className = '', ...props }) => (
  <div className={`mb-4 ${className}`} {...props}>
    {children}
  </div>
)

export const CardTitle: React.FC<CardComponentProps> = ({ children, className = '', ...props }) => (
  <h3 className={`text-xl font-bold text-gray-900 dark:text-white ${className}`} {...props}>
    {children}
  </h3>
)

export const CardDescription: React.FC<CardComponentProps> = ({ children, className = '', ...props }) => (
  <p className={`mt-1 text-sm text-gray-600 dark:text-gray-300 ${className}`} {...props}>
    {children}
  </p>
)

export const CardContent: React.FC<CardComponentProps> = ({ children, className = '', ...props }) => (
  <div className={`${className}`} {...props}>
    {children}
  </div>
)

export const CardFooter: React.FC<CardComponentProps> = ({ children, className = '', ...props }) => (
  <div className={`mt-4 pt-3 flex justify-end border-t border-gray-100 dark:border-gray-700 ${className}`} {...props}>
    {children}
  </div>
)