import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";
import ErrorBoundary from "@/components/ErrorBoundary";
import { TooltipProvider } from "@/components/ui/tooltip";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "VL Novel AI - 한국어 창작 AI 어시스턴트",
  description: "기가차드 파워로 한국어 소설을 자동 생성하는 AI 어시스턴트. 판타지, 로맨스, SF, 미스터리, 드라마 등 다양한 장르의 창작을 지원합니다.",
  keywords: ["AI", "소설", "창작", "한국어", "VL Novel", "자동생성", "기가차드"],
  authors: [{ name: "VL Novel AI Team" }],
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body
        className={`${inter.variable} antialiased bg-white dark:bg-gray-900 text-gray-900 dark:text-white transition-colors duration-300`}
      >
        <ErrorBoundary>
        <ThemeProvider>
          <TooltipProvider>
            {children}
          </TooltipProvider>
        </ThemeProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
