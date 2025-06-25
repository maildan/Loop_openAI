# 🚀 Loop AI - 창작 AI 플랫폼

한국어 특화 창작 전문 AI 플랫폼으로, 소설·시나리오·캐릭터 개발을 지원합니다.

## ✨ 주요 기능

### 🎯 핵심 AI 기능
- **창작 지원**: 소설, 시나리오, 캐릭터 설정 전문 AI
- **맞춤법 검사**: 한국어 전용 고급 맞춤법 및 문법 검사
- **판타지 이름 생성**: 다양한 장르별 캐릭터명 자동 생성
- **스토리 생성**: 장르별 맞춤 스토리 아이디어 제공

### 🔍 새로운 검색 기능
- **웹 검색**: MCP Exa Search 기반 실시간 웹 검색
  - 일반 웹 페이지 검색
  - 학술 논문 및 연구 자료 검색  
  - 위키피디아 백과사전 검색
  - GitHub 코드 및 프로젝트 검색
  - 기업 정보 검색
- **AI 요약**: 검색 결과의 자동 요약 및 링크 제공
- **Redis 캐싱**: 10분 TTL로 성능 최적화

### 🌍 위치 추천 기능
- **Neutrino API 연동**: 실시간 지역·도시명 추천
- **한국어 지원**: 한국어 기반 위치 검색
- **여행 계획**: 관광지 및 여행 목적지 추천

## 🏗️ 아키텍처

### 백엔드 (FastAPI)
```
src/inference/api/
├── server.py              # 메인 서버
├── handlers/
│   ├── chat_handler.py    # 채팅 AI 핸들러
│   ├── spellcheck_handler.py  # 맞춤법 검사
│   ├── location_handler.py    # 위치 추천 (Neutrino API)
│   └── web_search_handler.py  # 웹 검색 (MCP Exa)
└── utils/
    ├── fantasy_name_generator.py
    └── spellcheck.py
```

### 프론트엔드 (Next.js 14)
```
frontend/src/
├── app/
│   ├── page.tsx           # 메인 채팅 인터페이스
│   └── api/chat/route.ts  # API 라우트
└── components/ui/
    ├── WebSearchButton.tsx    # 웹 검색 모달
    ├── Button.tsx
    └── Card.tsx
```

## 🚀 설치 및 실행

### 1. 환경 설정
```bash
# 저장소 클론
git clone <repository-url>
cd loop_ai

# Python 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
export OPENAI_API_KEY="your-openai-api-key"
export KEY_TAG="your-neutrino-user-id"      # Neutrino API
export KEY="your-neutrino-api-key"          # Neutrino API
export REDIS_URL="redis://localhost:6379"   # Redis (선택사항)
```

### 2. 백엔드 서버 실행
```bash
# 메인 서버 실행
python run_server.py

# 또는 직접 실행
python -m src.inference.api.server
```

### 3. 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```

### 4. 접속
- 프론트엔드: http://localhost:3000
- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/api/health

## 🔧 API 엔드포인트

### 채팅 AI
```http
POST /api/chat
{
  "message": "판타지 소설 시놉시스를 작성해주세요",
  "history": [],
  "model": "gpt-4o-mini"
}
```

### 웹 검색
```http
POST /api/web-search
{
  "query": "FastAPI 성능 최적화",
  "source": "web",
  "num_results": 5,
  "include_summary": true
}
```

### 위치 추천
```http
POST /api/location-suggest
{
  "query": "제주도 여행지"
}
```

### 맞춤법 검사
```http
POST /api/spellcheck
{
  "text": "안녕하세요 오늘은 좋은날씨네요"
}
```

### 판타지 이름 생성
```http
POST /api/fantasy-names
{
  "genre": "fantasy",
  "gender": "mixed",
  "count": 10
}
```

## 🎯 사용 예시

### 1. 창작 지원
```
사용자: "마법학교를 배경으로 한 판타지 소설 시놉시스를 작성해주세요"
AI: 상세한 시놉시스 및 캐릭터 설정 제공
```

### 2. 웹 검색 + AI 요약
```
사용자: "최신 AI 트렌드에 대해 검색해줘"
시스템: 실시간 웹 검색 → AI 요약 → 관련 링크 제공
```

### 3. 위치 추천
```
사용자: "부산 여행지 추천해줘"
시스템: Neutrino API → 부산 관광지 목록 반환
```

## 🔥 성능 최적화

### Redis 캐싱
- 웹 검색 결과 10분 캐싱
- 캐시 히트율 통계 제공
- 메모리 기반 고속 응답

### 비동기 처리
- FastAPI 비동기 엔드포인트
- aioredis 비동기 Redis 클라이언트
- 동시 요청 처리 최적화

### 비용 최적화
- GPT-3.5-turbo 사용으로 비용 절약
- 토큰 사용량 실시간 추적
- 예산 초과 시 자동 모델 전환

## 📊 모니터링

### 통계 조회
```http
GET /api/web-search/stats
{
  "total_searches": 150,
  "cache_hits": 45,
  "cache_hit_rate": "30.0%",
  "avg_response_time": 1.23
}
```

### 헬스체크
```http
GET /api/health
{
  "status": "healthy",
  "web_search": {"enabled": true, "cache_enabled": true},
  "location": {"enabled": true},
  "spellcheck": {"enabled": true}
}
```

## 🛠️ 기술 스택

### 백엔드
- **FastAPI**: 고성능 Python 웹 프레임워크
- **OpenAI GPT**: 창작 AI 엔진
- **MCP Exa Search**: 실시간 웹 검색
- **Neutrino API**: 지역 정보 서비스
- **Redis**: 캐싱 및 세션 관리
- **Pydantic**: 데이터 검증

### 프론트엔드
- **Next.js 14**: React 기반 풀스택 프레임워크
- **TypeScript**: 타입 안전성
- **Tailwind CSS**: 유틸리티 우선 CSS
- **Lucide React**: 아이콘 라이브러리

### 데이터
- **JSON**: 대화 데이터셋
- **한국어 사전**: NIA 표준 한국어 대사전
- **캐릭터 데이터**: 한국 전통 이름 및 성격 데이터

## 🤝 기여하기

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🔗 관련 링크

- [OpenAI API 문서](https://platform.openai.com/docs)
- [Neutrino API 문서](https://www.neutrinoapi.com/api/)
- [MCP Exa Search](https://docs.exa.ai/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Next.js 문서](https://nextjs.org/docs)

---

**🔥 기가차드급 AI로 창작의 새로운 경험을 시작하세요!** 🚀

## MCP 서버 설정

Loop AI는 Model Context Protocol (MCP)을 지원합니다. 이를 통해 웹 검색 기능을 외부 LLM 애플리케이션에 통합할 수 있습니다.

### MCP 서버 활성화

1. MCP 관련 패키지 설치:

```bash
pip install mcp-python mcp-client
```

2. `src/inference/api/server.py` 파일에서 MCP 서버 설정 활성화:

```python
# MCP 서버 초기화 (주석 해제)
mcp_server = FastMCP("loop_ai", stateless_http=True)
logger.info("✅ MCP 서버 초기화 완료")
```

3. 서버 재시작 후 MCP 엔드포인트 확인:

```bash
curl -X GET http://localhost:8080/mcp
```

### MCP 클라이언트 설정

Claude Desktop이나 Q CLI에서 Loop AI MCP 서버를 사용하려면 다음 설정을 사용하세요:

```json
{
  "mcpServers": {
    "loop_ai": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8080/mcp/"
      ]
    }
  }
}
```

자세한 내용은 [MCP 설정 가이드](docs/MCP_SETUP_GUIDE.md)를 참조하세요.

## API 문서

서버 실행 후 `http://localhost:8080/docs`에서 API 문서를 확인할 수 있습니다.
# Loop_openAI
