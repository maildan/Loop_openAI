# Web Search API Documentation

Loop AI의 웹 검색 API는 [Exa AI](https://exa.ai)를 기반으로 한 강력한 검색 기능을 제공합니다. 다양한 소스에서 정보를 검색하고 AI가 생성한 요약을 제공합니다.

## 🔍 개요

웹 검색 API는 다음과 같은 기능을 제공합니다:

- **다중 소스 검색**: 웹, 학술 논문, Wikipedia, GitHub, 회사 정보
- **AI 요약**: 검색 결과의 자동 요약 및 분석  
- **Redis 캐싱**: 빠른 응답을 위한 캐시 시스템
- **실시간 검색**: 최신 정보 제공
- **통계 추적**: 검색 성능 및 사용량 모니터링

## 📡 API 엔드포인트

### 1. 웹 검색 (`POST /api/web-search`)

#### 요청 형식
```http
POST /api/web-search
Content-Type: application/json

{
  "query": "검색어",
  "source": "web",
  "num_results": 5,
  "include_summary": true
}
```

#### 매개변수

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `query` | string | ✅ | - | 검색할 쿼리 |
| `source` | string | ❌ | "web" | 검색 소스 |
| `num_results` | integer | ❌ | 5 | 결과 개수 (1-10) |
| `include_summary` | boolean | ❌ | true | AI 요약 포함 여부 |

#### 지원되는 소스

| 소스 | 설명 | 예시 |
|------|------|------|
| `web` | 일반 웹 검색 | 뉴스, 블로그, 일반 웹사이트 |
| `research` | 학술 논문 검색 | arXiv, PubMed, 학술지 |
| `wiki` | Wikipedia 검색 | 백과사전 정보 |
| `github` | GitHub 저장소 검색 | 오픈소스 프로젝트, 코드 |
| `company` | 회사 정보 검색 | 기업 정보, 재무 데이터 |

#### 응답 형식
```json
{
  "query": "인공지능 최신 동향",
  "source": "web",
  "num_results": 3,
  "results": [
    {
      "title": "2025년 AI 기술 전망",
      "url": "https://example.com/ai-trends-2025",
      "snippet": "인공지능 기술이 급속도로 발전하고 있으며...",
      "publishedDate": "2025-01-15",
      "favicon": "https://example.com/favicon.ico"
    }
  ],
  "summary": "2025년 인공지능 분야에서는 대규모 언어 모델의 발전과 함께...",
  "timestamp": "2025-06-26T01:31:20.105029",
  "from_cache": false,
  "response_time": 3.2
}
```

### 2. 검색 통계 (`GET /api/web-search/stats`)

#### 요청 형식
```http
GET /api/web-search/stats
```

#### 응답 형식
```json
{
  "total_searches": 1247,
  "cache_hits": 892,
  "cache_hit_rate": 71.5,
  "average_response_time": 3.4,
  "searches_by_source": {
    "web": 756,
    "research": 234,
    "wiki": 157,
    "github": 89,
    "company": 11
  },
  "recent_searches": [
    {
      "query": "최신 AI 뉴스",
      "source": "web",
      "timestamp": "2025-06-26T01:30:15.123456",
      "response_time": 2.8,
      "from_cache": false
    }
  ]
}
```

### 3. 캐시 클리어 (`DELETE /api/web-search/cache`)

#### 요청 형식
```http
DELETE /api/web-search/cache
```

#### 응답 형식
```json
{
  "success": true,
  "message": "캐시가 클리어되었습니다"
}
```

## 💻 사용 예제

### JavaScript/Node.js
```javascript
// 기본 웹 검색
const searchWeb = async (query) => {
  const response = await fetch('http://localhost:8080/api/web-search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      source: 'web',
      num_results: 5,
      include_summary: true
    })
  });
  
  const data = await response.json();
  return data;
};

// 학술 논문 검색
const searchResearch = async (topic) => {
  const response = await fetch('http://localhost:8080/api/web-search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: topic,
      source: 'research',
      num_results: 3,
      include_summary: true
    })
  });
  
  return await response.json();
};

// 사용 예시
const results = await searchWeb('ChatGPT 최신 업데이트');
console.log('검색 결과:', results.results);
console.log('AI 요약:', results.summary);
```

### Python
```python
import requests

def search_web(query, source='web', num_results=5):
    """웹 검색 함수"""
    response = requests.post(
        'http://localhost:8080/api/web-search',
        json={
            'query': query,
            'source': source,
            'num_results': num_results,
            'include_summary': True
        }
    )
    return response.json()

def get_search_stats():
    """검색 통계 조회"""
    response = requests.get('http://localhost:8080/api/web-search/stats')
    return response.json()

# 사용 예시
# 일반 웹 검색
web_results = search_web('파이썬 머신러닝 튜토리얼')
print(f"검색 결과 수: {len(web_results['results'])}")
print(f"AI 요약: {web_results['summary']}")

# GitHub 검색
github_results = search_web('FastAPI 예제', source='github', num_results=3)
for result in github_results['results']:
    print(f"- {result['title']}: {result['url']}")

# 통계 확인
stats = get_search_stats()
print(f"총 검색 수: {stats['total_searches']}")
print(f"캐시 적중률: {stats['cache_hit_rate']}%")
```

### cURL
```bash
# 기본 웹 검색
curl -X POST "http://localhost:8080/api/web-search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "React 18 새로운 기능",
    "source": "web",
    "num_results": 3,
    "include_summary": true
  }' | jq .

# Wikipedia 검색
curl -X POST "http://localhost:8080/api/web-search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "인공지능",
    "source": "wiki",
    "num_results": 1,
    "include_summary": true
  }' | jq '.summary'

# 검색 통계 조회
curl -X GET "http://localhost:8080/api/web-search/stats" | jq .

# 캐시 클리어
curl -X DELETE "http://localhost:8080/api/web-search/cache" | jq .
```

## ⚡ 성능 최적화

### Redis 캐싱
- **캐시 키**: 쿼리, 소스, 결과 개수를 조합한 해시
- **TTL**: 1시간 (3600초)
- **캐시 적중률**: 평균 70% 이상
- **응답 시간**: 캐시 적중 시 <100ms

### 응답 시간 최적화
```python
# 캐시 우선 검색 패턴
async def optimized_search(query, source='web'):
    # 1. 캐시 확인
    cached_result = await redis_client.get(cache_key)
    if cached_result:
        return json.loads(cached_result)
    
    # 2. 실제 검색 수행
    result = await exa_search(query, source)
    
    # 3. 캐시에 저장
    await redis_client.setex(cache_key, 3600, json.dumps(result))
    
    return result
```

## 🚨 에러 처리

### 일반적인 에러

| 상태 코드 | 에러 | 해결 방법 |
|-----------|------|-----------|
| 400 | `Invalid source` | 지원되는 소스 사용 |
| 400 | `num_results out of range` | 1-10 범위로 설정 |
| 503 | `Web search service unavailable` | 서비스 재시작 또는 대기 |
| 500 | `Exa API error` | API 키 확인 또는 재시도 |

### 에러 응답 예시
```json
{
  "detail": "Invalid source 'invalid'. Supported sources: web, research, wiki, github, company"
}
```

## 🔧 설정

### 환경 변수
```bash
# Exa AI API 설정
EXA_API_KEY=your_exa_api_key

# Redis 설정 (선택사항)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_password

# 검색 제한 설정
MAX_SEARCH_RESULTS=10
SEARCH_TIMEOUT=30
```

### 고급 설정
```python
# server.py에서 설정 가능한 옵션들
WEB_SEARCH_CONFIG = {
    "default_num_results": 5,
    "max_num_results": 10,
    "cache_ttl": 3600,  # 1시간
    "timeout": 30,      # 30초
    "retry_attempts": 3
}
```

## 📊 모니터링

### 성능 메트릭
- **응답 시간**: 평균 3-4초
- **캐시 적중률**: 70% 이상
- **성공률**: 99% 이상
- **동시 요청**: 최대 100개

### 로그 예시
```
2025-06-26 01:31:20 - INFO - 웹 검색 요청: query="AI 뉴스", source=web, results=5
2025-06-26 01:31:23 - INFO - 검색 완료: response_time=3.2s, from_cache=false
2025-06-26 01:31:23 - INFO - 캐시 저장: key=web_ai뉴스_5, ttl=3600s
```

## 🔄 업데이트 이력

### v2.0.0 (2025-06-26)
- ✅ 웹 검색 API 최초 출시
- ✅ 5개 소스 지원 (web, research, wiki, github, company)
- ✅ Redis 캐싱 시스템 구현
- ✅ AI 요약 기능 추가
- ✅ 통계 및 모니터링 기능

---

**관련 문서**:
- [API 메인 문서](./README.md)
- [에러 처리 가이드](./troubleshooting.md)
- [예제 코드](./examples.md) 