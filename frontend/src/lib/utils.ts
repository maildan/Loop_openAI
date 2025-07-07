import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

// 백엔드 서버 URL
export const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8080"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
} 