export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ')
}

// 백엔드 서버 URL (포트 8080)
export const baseUrl = "http://localhost:8080" 