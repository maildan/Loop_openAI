# Loop AI API Documentation

Loop AI는 한국어 창작, 웹 검색, 맞춤법 검사, Google Docs 연동을 위한 고성능 AI API입니다. 이 문서는 개발자들이 Loop AI API를 효율적으로 활용할 수 있도록 상세한 가이드를 제공합니다.

## 📋 목차

- [개요](#개요)
- [시작하기](#시작하기)
- [인증](#인증)
- [API 엔드포인트](#api-엔드포인트)
- [에러 처리](#에러-처리)
- [Rate Limiting](#rate-limiting)
- [예제 코드](#예제-코드)
- [변경 이력](#변경-이력)

## 🎯 개요

Loop AI API는 다음과 같은 주요 기능을 제공합니다:

### 🤖 AI 채팅 및 창작
- **의도별 처리**: 창작, 인사, 질문 등 사용자 의도 자동 감지
- **레벨별 최적화**: 초보자, 중급자, 고급자에 맞는 맞춤형 응답
- **긴 소설 모드**: 최대 8,000 토큰의 장편 소설 생성
- **이야기 계속하기**: 미완성 응답 자동 감지 및 연속 생성
- **실시간 비용 추적**: OpenAI API 사용량 및 비용 모니터링

### 🔍 웹 검색 통합
- **다중 소스 검색**: 일반 웹, 학술 논문, Wikipedia, GitHub, 회사 정보
- **AI 요약**: 검색 결과의 자동 요약 및 분석
- **Redis 캐싱**: 빠른 응답을 위한 캐시 시스템
- **실시간 검색**: 최신 정보 제공

### ✍️ 맞춤법 검사
- **한국어 특화**: 50,000개 단어 사전 기반
- **자동 수정**: 맞춤법 오류 자동 감지 및 수정
- **통계 제공**: 정확도, 오류 개수 등 상세 통계

### 📄 Google Docs 연동
- **문서 생성**: 새 Google 문서 생성
- **문서 읽기**: 기존 문서 내용 추출
- **문서 업데이트**: 실시간 문서 편집
- **문서 분석**: AI 기반 문서 내용 분석
- **스토리 생성**: 문서 기반 창작 지원

### 🌍 위치 추천
- **지역 검색**: 도시, 지역명 자동 완성
- **Neutrino API 연동**: 정확한 위치 정보 제공

## 🚀 시작하기

### Base URL
```
Development: http://localhost:8080
Production: https://api.loop-ai.com (예정)
```

### API 버전
현재 API 버전: **v2.0.0**

### 필수 요구사항
- **Content-Type**: `application/json`
- **Accept**: `application/json`
- **User-Agent**: 클라이언트 식별을 위한 적절한 User-Agent 헤더

### 빠른 시작 예제

```bash
# Health Check
curl -X GET "http://localhost:8080/api/health"

# AI 채팅
curl -X POST "http://localhost:8080/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "판타지 소설 써줘",
    "history": [],
    "maxTokens": 2000,
    "isLongForm": false,
    "continueStory": false
  }'

# 웹 검색
curl -X POST "http://localhost:8080/api/web-search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "최신 AI 뉴스",
    "source": "web",
    "num_results": 5,
    "include_summary": true
  }'
```

## 🔐 인증

현재 Loop AI API는 **오픈 액세스**로 제공됩니다. 향후 API 키 기반 인증이 추가될 예정입니다.

### 향후 인증 방식 (예정)
```http
Authorization: Bearer YOUR_API_KEY
```

## 📡 API 엔드포인트

### 🏥 시스템 상태
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | API 서버 상태 확인 |
| GET | `/api/cost-status` | 비용 및 사용량 상태 조회 |

### 🤖 AI 채팅 및 창작
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | 메인 채팅 엔드포인트 (창작, 질문, 대화) |

#### `/api/chat` 요청 형식
```json
{
  "message": "사용자 메시지",
  "history": [
    {
      "role": "user",
      "content": "이전 메시지"
    },
    {
      "role": "assistant", 
      "content": "AI 응답"
    }
  ],
  "maxTokens": 4000,
  "isLongForm": false,
  "continueStory": false
}
```

#### `/api/chat` 응답 형식
```json
{
  "response": "AI 생성 응답",
  "model": "gpt-4o-mini",
  "cost": 0.00024,
  "tokens": 552,
  "isComplete": true,
  "continuationToken": null
}
```

### 🔍 웹 검색
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/web-search` | 웹 검색 및 AI 요약 |
| GET | `/api/web-search/stats` | 웹 검색 통계 조회 |
| DELETE | `/api/web-search/cache` | 웹 검색 캐시 클리어 |

#### `/api/web-search` 요청 형식
```json
{
  "query": "검색어",
  "source": "web",
  "num_results": 5,
  "include_summary": true
}
```

**지원되는 소스:**
- `web`: 일반 웹 검색
- `research`: 학술 논문 검색
- `wiki`: Wikipedia 검색
- `github`: GitHub 저장소 검색
- `company`: 회사 정보 검색

#### `/api/web-search` 응답 형식
```json
{
  "query": "검색어",
  "source": "web",
  "num_results": 5,
  "results": [
    {
      "title": "제목",
      "url": "https://example.com",
      "snippet": "요약 내용",
      "publishedDate": "2025-01-01",
      "favicon": "https://example.com/favicon.ico"
    }
  ],
  "summary": "AI 생성 요약",
  "timestamp": "2025-06-26T01:31:20.105029",
  "from_cache": false,
  "response_time": 3.2
}
```

### ✍️ 맞춤법 검사
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/spellcheck` | 맞춤법 검사 및 자동 수정 |
| GET | `/api/spellcheck/stats` | 맞춤법 검사기 통계 |

#### `/api/spellcheck` 요청 형식
```json
{
  "text": "검사할 텍스트",
  "auto_correct": true
}
```

#### `/api/spellcheck` 응답 형식
```json
{
  "success": true,
  "original_text": "원본 텍스트",
  "corrected_text": "수정된 텍스트",
  "errors_found": 3,
  "error_words": ["틀린단어1", "틀린단어2"],
  "accuracy": 95.5,
  "total_words": 20
}
```

### 🌍 위치 추천
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/location-suggest` | 지역·도시명 추천 |

#### `/api/location-suggest` 요청 형식
```json
{
  "query": "검색할 지역명"
}
```

#### `/api/location-suggest` 응답 형식
```json
{
  "suggestions": [
    "서울특별시",
    "서울역",
    "서울대학교"
  ]
}
```

### 📄 Google Docs 연동
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/docs/create` | 새 Google 문서 생성 |
| GET | `/api/docs/{document_id}` | 문서 내용 가져오기 |
| PUT | `/api/docs/{document_id}` | 문서 내용 업데이트 |
| POST | `/api/docs/analyze` | 문서 내용 분석 |
| POST | `/api/docs/generate-story` | 문서 기반 스토리 생성 |

#### Google Docs API 사용 시 주의사항
- Google OAuth2 인증이 필요합니다
- 환경 변수에 Google API 키가 설정되어 있어야 합니다:
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - `GOOGLE_ACCESS_TOKEN`
  - `GOOGLE_REFRESH_TOKEN`

## ⚠️ 에러 처리

모든 API 응답은 표준 HTTP 상태 코드를 사용합니다:

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | 요청 성공 |
| 201 | Created | 리소스 생성 성공 |
| 400 | Bad Request | 잘못된 요청 파라미터 |
| 401 | Unauthorized | 인증 실패 |
| 403 | Forbidden | 권한 부족 |
| 404 | Not Found | 엔드포인트를 찾을 수 없음 |
| 422 | Unprocessable Entity | 유효성 검사 실패 |
| 429 | Too Many Requests | Rate limit 초과 |
| 500 | Internal Server Error | 서버 내부 오류 |
| 503 | Service Unavailable | 서비스 일시 중단 |

### 에러 응답 형식
```json
{
  "detail": "서버 내부 오류: 구체적인 오류 메시지"
}
```

## 🛡️ Rate Limiting

현재 Rate Limiting은 구현되지 않았지만, 향후 다음과 같은 제한이 적용될 예정입니다:

- **무료 사용자**: 100 요청/시간
- **프리미엄 사용자**: 1,000 요청/시간
- **엔터프라이즈**: 제한 없음

## 💻 예제 코드

### JavaScript/Node.js
```javascript
// AI 채팅
const chatResponse = await fetch('http://localhost:8080/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: '로맨스 소설 써줘',
    history: [],
    maxTokens: 2000,
    isLongForm: true,
    continueStory: false
  })
});

const chatData = await chatResponse.json();
console.log(chatData.response);

// 웹 검색
const searchResponse = await fetch('http://localhost:8080/api/web-search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: '인공지능 최신 동향',
    source: 'web',
    num_results: 3,
    include_summary: true
  })
});

const searchData = await searchResponse.json();
console.log(searchData.summary);
```

### Python
```python
import requests

# AI 창작
response = requests.post(
    'http://localhost:8080/api/chat',
    json={
        'message': 'SF 소설 써줘',
        'history': [],
        'maxTokens': 3000,
        'isLongForm': True,
        'continueStory': False
    }
)

chat_data = response.json()
print(chat_data['response'])

# 맞춤법 검사
spellcheck_response = requests.post(
    'http://localhost:8080/api/spellcheck',
    json={
        'text': '안녕하세요. 맞춤법을 검사해주세요.',
        'auto_correct': True
    }
)

spellcheck_data = spellcheck_response.json()
print(f"수정된 텍스트: {spellcheck_data['corrected_text']}")
print(f"정확도: {spellcheck_data['accuracy']}%")
```

### cURL
```bash
# 비용 상태 확인
curl -X GET "http://localhost:8080/api/cost-status" | jq .

# 웹 검색 통계
curl -X GET "http://localhost:8080/api/web-search/stats" | jq .

# 위치 추천
curl -X POST "http://localhost:8080/api/location-suggest" \
  -H "Content-Type: application/json" \
  -d '{"query": "강남"}' | jq .
```

## 🔧 기술 스택

- **백엔드**: FastAPI, Python 3.10+
- **AI 모델**: OpenAI GPT-4o-mini
- **웹 검색**: Exa AI API
- **캐싱**: Redis
- **문서 연동**: Google Docs API
- **맞춤법**: 커스텀 한국어 사전 (50,000 단어)

## 📊 성능 지표

- **평균 응답 시간**:
  - 기본 채팅: ~7초
  - 창작 요청: ~15초
  - 웹 검색: ~4초
  - 헬스 체크: <1초
- **비용 효율성**: 예산 대비 0.005% 사용
- **토큰 최적화**: 동적 토큰 할당 시스템

## 🔄 변경 이력

### v2.0.0 (2025-06-26)
- ✅ **새로운 기능**
  - 웹 검색 API 추가 (`/api/web-search`)
  - 맞춤법 검사 API 추가 (`/api/spellcheck`)
  - Google Docs 연동 API 추가 (`/api/docs/*`)
  - 위치 추천 API 추가 (`/api/location-suggest`)
  - 비용 상태 조회 API 추가 (`/api/cost-status`)
- 🔧 **개선사항**
  - 의도별 분기 처리 구현
  - 레벨별 창작 최적화
  - 실시간 비용 추적
  - Redis 캐싱 시스템
  - 에러 처리 강화
- 🐛 **버그 수정**
  - ChatHandler.handle_request() 매개변수 오류 수정
  - Pyright 정적 분석 경고 해결
  - API 응답 형식 표준화

### v1.0.0 (이전 버전)
- 기본 Fantasy Name Generator
- 기본 Story Generator
- Health Check API

---

**개발팀**: Loop AI Team  
**문서 업데이트**: 2025-06-26  
**API 버전**: v2.0.0 