# 🤖 VL Novel AI Frontend

기가차드 파워로 작동하는 한국어 창작 AI 어시스턴트의 프론트엔드입니다! 💪

## ✨ 주요 기능

- **🎨 현대적인 UI/UX**: Tailwind CSS 기반의 반응형 디자인
- **🚀 실시간 소설 생성**: VL Novel 파인튜닝된 모델 활용
- **🎭 다양한 장르**: 판타지, 로맨스, SF, 미스터리, 드라마
- **⚙️ 커스터마이징**: 창의성과 길이 조절 가능
- **📝 예시 프롬프트**: 클릭 한 번으로 빠른 시작
- **💾 내보내기**: 텍스트 복사 및 파일 다운로드

## 🛠️ 기술 스택

- **Frontend**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS 4
- **Language**: TypeScript
- **Package Manager**: pnpm
- **Backend Communication**: FastAPI REST API

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
pnpm install
```

### 2. 개발 서버 실행 (프론트엔드만)
```bash
pnpm dev
```

### 3. 풀스택 실행 (FastAPI + Next.js 동시)
```bash
pnpm run dev:all
```

### 4. FastAPI 서버만 실행
```bash
pnpm run fastapi
```

## 📁 프로젝트 구조

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # 루트 레이아웃
│   │   ├── page.tsx           # 메인 페이지
│   │   └── globals.css        # 글로벌 스타일
│   ├── components/
│   │   ├── StoryGenerator.tsx # 메인 소설 생성 컴포넌트
│   │   └── ui/                # 재사용 가능한 UI 컴포넌트
│   │       ├── Button.tsx     # 버튼 컴포넌트
│   │       └── Card.tsx       # 카드 컴포넌트
│   ├── hooks/
│   │   └── useStoryGeneration.ts # API 통신 훅
│   └── lib/
│       └── utils.ts           # 유틸리티 함수
├── public/                    # 정적 파일
├── package.json              # 의존성 및 스크립트
├── next.config.ts            # Next.js 설정 (FastAPI 연동)
├── tailwind.config.ts        # Tailwind 설정
└── tsconfig.json             # TypeScript 설정
```

## 🎯 주요 컴포넌트

### StoryGenerator
- 메인 소설 생성 인터페이스
- 프롬프트 입력, 장르 선택, 파라미터 조정
- 실시간 결과 표시 및 내보내기

### Custom Hooks
- `useStoryGeneration`: 소설 생성 API 호출
- `useGenres`: 장르 목록 관리
- `useExamples`: 예시 프롬프트 관리

## 🌐 API 연동

Next.js의 `rewrites` 기능을 통해 FastAPI 서버와 통신:

```typescript
// next.config.ts
rewrites: async () => {
  return [
    {
      source: "/api/:path*",
      destination: "http://127.0.0.1:8000/api/:path*", // 개발 환경
    }
  ];
}
```

## 🎨 스타일링

- **Tailwind CSS 4**: 최신 버전 사용
- **반응형 디자인**: 모바일부터 데스크톱까지
- **다크 모드 준비**: 쉬운 확장 가능
- **그라데이션 배경**: 보라-파랑-인디고 그라데이션

## 🔧 환경 설정

### 개발 환경
- Node.js 18+
- pnpm 8+
- TypeScript 5+

### 환경 변수
```env
NEXT_PUBLIC_API_URL=http://localhost:8000  # FastAPI 서버 URL
```

## 🚀 배포

### Vercel 배포
1. GitHub에 푸시
2. Vercel과 연결
3. 자동 배포 완료

### 수동 빌드
```bash
pnpm build
pnpm start
```

## 🤝 기여하기

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

MIT License

## 🎉 기가차드 개발자를 위한 팁

- **빠른 개발**: `pnpm run dev:all`로 풀스택 개발
- **모듈화**: 컴포넌트는 재사용 가능하게 설계
- **타입 안정성**: TypeScript 완전 활용
- **성능 최적화**: Next.js App Router 최적화

---

기가차드 파워로 만든 VL Novel AI! 🚀💪
