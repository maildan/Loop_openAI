import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 백엔드 서버 URL (포트 8080)
export const baseUrl = "http://localhost:8080" 