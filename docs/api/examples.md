# Loop AI API 예제 코드

이 문서는 Loop AI API의 다양한 기능을 활용하는 실제 예제 코드를 제공합니다.

## 📋 목차

- [기본 설정](#기본-설정)
- [AI 채팅 및 창작](#ai-채팅-및-창작)
- [웹 검색](#웹-검색)
- [맞춤법 검사](#맞춤법-검사)
- [Google Docs 연동](#google-docs-연동)
- [위치 추천](#위치-추천)
- [통합 예제](#통합-예제)
- [에러 처리](#에러-처리)

## 🚀 기본 설정

### JavaScript/Node.js 설정
```javascript
// config.js
const API_BASE_URL = 'http://localhost:8080';

// API 클라이언트 클래스
class LoopAIClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`API 요청 실패: ${error.message}`);
      throw error;
    }
  }
}

const client = new LoopAIClient();
```

### Python 설정
```python
# client.py
import requests
import json
from typing import Dict, List, Optional

class LoopAIClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """API 요청 헬퍼 메소드"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            raise

client = LoopAIClient()
```

## 🤖 AI 채팅 및 창작

### 1. 기본 채팅
```javascript
// 기본 채팅 예제
async function basicChat(message) {
  const response = await client.request('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      message: message,
      history: [],
      maxTokens: 1000,
      isLongForm: false,
      continueStory: false
    })
  });
  
  console.log('AI 응답:', response.response);
  console.log('사용된 토큰:', response.tokens);
  console.log('비용:', response.cost);
  
  return response;
}

// 사용 예시
await basicChat('안녕하세요! 오늘 기분이 어떠세요?');
```

### 2. 창작 요청
```python
# 판타지 소설 생성
def generate_fantasy_story(prompt: str, is_long_form: bool = False):
    response = client.request('POST', '/api/chat', json={
        'message': f'판타지 소설 써줘: {prompt}',
        'history': [],
        'maxTokens': 4000 if is_long_form else 2000,
        'isLongForm': is_long_form,
        'continueStory': False
    })
    
    print(f"생성된 소설 ({response['tokens']} 토큰):")
    print(response['response'])
    print(f"비용: ${response['cost']:.4f}")
    
    return response

# 사용 예시
story = generate_fantasy_story('용과 마법사의 모험', is_long_form=True)
```

### 3. 대화 히스토리 유지
```javascript
// 대화 히스토리를 유지하는 채팅봇
class ChatBot {
  constructor() {
    this.history = [];
  }

  async chat(message) {
    const response = await client.request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: message,
        history: this.history,
        maxTokens: 1500,
        isLongForm: false,
        continueStory: false
      })
    });

    // 히스토리에 추가
    this.history.push(
      { role: 'user', content: message },
      { role: 'assistant', content: response.response }
    );

    // 히스토리가 너무 길어지면 앞부분 제거 (최근 10개 메시지만 유지)
    if (this.history.length > 20) {
      this.history = this.history.slice(-20);
    }

    return response;
  }

  clearHistory() {
    this.history = [];
  }
}

// 사용 예시
const bot = new ChatBot();
await bot.chat('로맨스 소설의 주인공 설정을 도와줘');
await bot.chat('주인공은 카페 사장이야');
await bot.chat('이제 스토리를 써줘');
```

### 4. 이야기 계속하기
```python
# 긴 소설을 여러 번에 걸쳐 생성
def generate_long_story(initial_prompt: str, max_parts: int = 5):
    story_parts = []
    current_message = initial_prompt
    
    for part in range(max_parts):
        print(f"파트 {part + 1} 생성 중...")
        
        response = client.request('POST', '/api/chat', json={
            'message': current_message,
            'history': [],
            'maxTokens': 3000,
            'isLongForm': True,
            'continueStory': part > 0
        })
        
        story_parts.append(response['response'])
        
        # 완성된 경우 중단
        if response.get('isComplete', True):
            print(f"소설이 완성되었습니다! (총 {part + 1}개 파트)")
            break
            
        # 다음 파트를 위한 메시지 설정
        current_message = "이야기를 계속 써줘"
    
    # 전체 소설 합치기
    full_story = '\n\n'.join(story_parts)
    print(f"총 길이: {len(full_story)} 글자")
    
    return full_story

# 사용 예시
long_story = generate_long_story('중세 시대 기사의 모험 이야기를 써줘')
```

## 🔍 웹 검색

### 1. 기본 웹 검색
```javascript
// 웹 검색 함수
async function webSearch(query, source = 'web', numResults = 5) {
  const response = await client.request('/api/web-search', {
    method: 'POST',
    body: JSON.stringify({
      query: query,
      source: source,
      num_results: numResults,
      include_summary: true
    })
  });

  console.log(`검색어: ${response.query}`);
  console.log(`검색 결과 (${response.results.length}개):`);
  
  response.results.forEach((result, index) => {
    console.log(`${index + 1}. ${result.title}`);
    console.log(`   URL: ${result.url}`);
    console.log(`   요약: ${result.snippet}`);
    console.log('');
  });

  console.log('AI 요약:');
  console.log(response.summary);
  
  return response;
}

// 사용 예시
await webSearch('ChatGPT 최신 업데이트', 'web', 3);
await webSearch('머신러닝 논문', 'research', 5);
await webSearch('FastAPI', 'github', 3);
```

### 2. 다중 소스 검색
```python
# 여러 소스에서 동시 검색
import asyncio
import aiohttp

async def multi_source_search(query: str, sources: List[str] = None):
    if sources is None:
        sources = ['web', 'research', 'wiki', 'github']
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for source in sources:
            task = search_single_source(session, query, source)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 정리
        combined_results = {}
        for source, result in zip(sources, results):
            if isinstance(result, Exception):
                print(f"{source} 검색 실패: {result}")
                combined_results[source] = None
            else:
                combined_results[source] = result
        
        return combined_results

async def search_single_source(session, query: str, source: str):
    url = "http://localhost:8080/api/web-search"
    payload = {
        'query': query,
        'source': source,
        'num_results': 3,
        'include_summary': True
    }
    
    async with session.post(url, json=payload) as response:
        return await response.json()

# 사용 예시
results = asyncio.run(multi_source_search('인공지능 윤리'))
for source, data in results.items():
    if data:
        print(f"\n=== {source.upper()} 검색 결과 ===")
        print(data['summary'])
```

### 3. 검색 결과 캐싱 활용
```javascript
// 캐시를 활용한 효율적인 검색
class SmartSearch {
  constructor() {
    this.searchHistory = new Map();
  }

  async search(query, source = 'web') {
    const cacheKey = `${source}:${query}`;
    
    // 로컬 캐시 확인
    if (this.searchHistory.has(cacheKey)) {
      console.log('로컬 캐시에서 결과 반환');
      return this.searchHistory.get(cacheKey);
    }

    // API 검색 수행
    const response = await client.request('/api/web-search', {
      method: 'POST',
      body: JSON.stringify({
        query: query,
        source: source,
        num_results: 5,
        include_summary: true
      })
    });

    // 캐시 상태 확인
    if (response.from_cache) {
      console.log('서버 캐시에서 결과 반환');
    } else {
      console.log('새로운 검색 수행');
    }

    // 로컬 캐시에 저장
    this.searchHistory.set(cacheKey, response);
    
    return response;
  }

  async getStats() {
    return await client.request('/api/web-search/stats');
  }

  async clearCache() {
    // 서버 캐시 클리어
    await client.request('/api/web-search/cache', { method: 'DELETE' });
    
    // 로컬 캐시 클리어
    this.searchHistory.clear();
    
    console.log('모든 캐시가 클리어되었습니다');
  }
}

// 사용 예시
const smartSearch = new SmartSearch();
await smartSearch.search('React 18 새로운 기능');
await smartSearch.search('React 18 새로운 기능'); // 캐시에서 반환
const stats = await smartSearch.getStats();
console.log(`캐시 적중률: ${stats.cache_hit_rate}`);
```

## ✍️ 맞춤법 검사

### 1. 기본 맞춤법 검사
```python
# 맞춤법 검사 함수
def check_spelling(text: str, auto_correct: bool = True):
    response = client.request('POST', '/api/spellcheck', json={
        'text': text,
        'auto_correct': auto_correct
    })
    
    if response['success']:
        print(f"원본: {response['original_text']}")
        print(f"수정: {response['corrected_text']}")
        print(f"오류 개수: {response['errors_found']}")
        print(f"정확도: {response['accuracy']:.1f}%")
        
        if response['error_words']:
            print(f"오류 단어: {', '.join(response['error_words'])}")
    else:
        print("맞춤법 검사 실패")
    
    return response

# 사용 예시
result = check_spelling("안녕하세요. 맞춤법을 검사해주세요.", auto_correct=True)
```

### 2. 배치 맞춤법 검사
```javascript
// 여러 텍스트를 한 번에 검사
async function batchSpellCheck(texts) {
  const results = [];
  
  for (const [index, text] of texts.entries()) {
    console.log(`${index + 1}/${texts.length} 검사 중...`);
    
    try {
      const response = await client.request('/api/spellcheck', {
        method: 'POST',
        body: JSON.stringify({
          text: text,
          auto_correct: true
        })
      });
      
      results.push({
        original: text,
        corrected: response.corrected_text,
        errors: response.errors_found,
        accuracy: response.accuracy
      });
      
    } catch (error) {
      console.error(`텍스트 ${index + 1} 검사 실패:`, error);
      results.push({ original: text, error: error.message });
    }
  }
  
  return results;
}

// 사용 예시
const texts = [
  '안녕하세요. 반갑습니다.',
  '오늘 날씨가 정말 좋네요.',
  '맞춤법 검사를 해주세요.'
];

const results = await batchSpellCheck(texts);
results.forEach((result, index) => {
  console.log(`텍스트 ${index + 1}:`);
  console.log(`  원본: ${result.original}`);
  console.log(`  수정: ${result.corrected}`);
  console.log(`  정확도: ${result.accuracy}%`);
});
```

## 📄 Google Docs 연동

### 1. 문서 생성 및 편집
```python
# Google Docs 클라이언트
class GoogleDocsClient:
    def __init__(self, loop_ai_client):
        self.client = loop_ai_client
    
    def create_document(self, title: str, content: str = ""):
        """새 문서 생성"""
        response = self.client.request('POST', '/api/docs/create', json={
            'title': title,
            'content': content
        })
        
        print(f"문서 생성됨: {response['document_id']}")
        print(f"URL: {response['document_url']}")
        
        return response
    
    def get_document(self, document_id: str):
        """문서 내용 가져오기"""
        response = self.client.request('GET', f'/api/docs/{document_id}')
        
        print(f"문서 제목: {response['title']}")
        print(f"내용 길이: {len(response['content'])} 글자")
        
        return response
    
    def update_document(self, document_id: str, content: str):
        """문서 내용 업데이트"""
        response = self.client.request('PUT', f'/api/docs/{document_id}', json={
            'content': content
        })
        
        print("문서가 업데이트되었습니다")
        return response
    
    def analyze_document(self, document_id: str):
        """문서 내용 분석"""
        response = self.client.request('POST', '/api/docs/analyze', json={
            'document_id': document_id
        })
        
        print(f"분석 결과: {response['analysis']}")
        return response

# 사용 예시
docs_client = GoogleDocsClient(client)

# 새 문서 생성
doc = docs_client.create_document(
    title="AI가 생성한 판타지 소설",
    content="이것은 AI가 생성한 판타지 소설의 시작입니다..."
)

# 문서 내용 가져오기
content = docs_client.get_document(doc['document_id'])

# 문서 분석
analysis = docs_client.analyze_document(doc['document_id'])
```

### 2. 문서 기반 스토리 생성
```javascript
// 기존 문서를 기반으로 스토리 생성
async function generateStoryFromDoc(documentId, prompt) {
  const response = await client.request('/api/docs/generate-story', {
    method: 'POST',
    body: JSON.stringify({
      document_id: documentId,
      prompt: prompt,
      max_tokens: 3000
    })
  });

  console.log('생성된 스토리:');
  console.log(response.generated_story);
  console.log(`토큰 사용량: ${response.tokens_used}`);
  
  return response;
}

// 사용 예시
const story = await generateStoryFromDoc(
  '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
  '이 문서의 내용을 바탕으로 로맨스 소설을 써줘'
);
```

## 🌍 위치 추천

### 1. 기본 위치 검색
```python
# 위치 추천 함수
def suggest_locations(query: str):
    response = client.request('POST', '/api/location-suggest', json={
        'query': query
    })
    
    print(f"'{query}' 검색 결과:")
    for suggestion in response['suggestions']:
        print(f"  - {suggestion}")
    
    return response['suggestions']

# 사용 예시
locations = suggest_locations('강남')
cafe_locations = suggest_locations('카페')
university_locations = suggest_locations('대학교')
```

### 2. 자동완성 기능
```javascript
// 실시간 자동완성
class LocationAutocomplete {
  constructor() {
    this.cache = new Map();
    this.debounceTimer = null;
  }

  async suggest(query, callback) {
    // 디바운싱 적용 (300ms)
    clearTimeout(this.debounceTimer);
    
    this.debounceTimer = setTimeout(async () => {
      if (query.length < 2) {
        callback([]);
        return;
      }

      // 캐시 확인
      if (this.cache.has(query)) {
        callback(this.cache.get(query));
        return;
      }

      try {
        const response = await client.request('/api/location-suggest', {
          method: 'POST',
          body: JSON.stringify({ query: query })
        });

        const suggestions = response.suggestions;
        this.cache.set(query, suggestions);
        callback(suggestions);

    } catch (error) {
        console.error('위치 검색 실패:', error);
        callback([]);
      }
    }, 300);
  }
}

// 사용 예시
const autocomplete = new LocationAutocomplete();

// 가상의 입력 이벤트
autocomplete.suggest('서울', (suggestions) => {
  console.log('자동완성 결과:', suggestions);
});
```

## 🔗 통합 예제

### 1. AI 창작 + 웹 검색 + 맞춤법 검사 통합
```python
# 종합 창작 도구
class ComprehensiveWriter:
    def __init__(self, client):
        self.client = client
    
    async def research_and_write(self, topic: str, genre: str = "판타지"):
        """리서치 후 창작하기"""
        print(f"1단계: '{topic}' 관련 자료 수집 중...")
        
        # 웹 검색으로 자료 수집
        search_response = self.client.request('POST', '/api/web-search', json={
            'query': f"{topic} {genre}",
            'source': 'web',
            'num_results': 3,
            'include_summary': True
        })
        
        research_summary = search_response['summary']
        print(f"수집된 자료: {research_summary[:100]}...")
        
        print("2단계: 소설 생성 중...")
        
        # 리서치 결과를 바탕으로 창작
        creation_prompt = f"""
        다음 자료를 참고하여 {genre} 소설을 써줘:
        
        리서치 자료: {research_summary}
        
        주제: {topic}
        """
        
        story_response = self.client.request('POST', '/api/chat', json={
            'message': creation_prompt,
            'history': [],
            'maxTokens': 4000,
            'isLongForm': True,
            'continueStory': False
        })
        
        generated_story = story_response['response']
        print(f"생성된 소설 길이: {len(generated_story)} 글자")
        
        print("3단계: 맞춤법 검사 중...")
        
        # 맞춤법 검사
        spellcheck_response = self.client.request('POST', '/api/spellcheck', json={
            'text': generated_story,
            'auto_correct': True
        })
        
        final_story = spellcheck_response['corrected_text']
        
        print("4단계: 완성!")
        print(f"최종 정확도: {spellcheck_response['accuracy']:.1f}%")
        print(f"수정된 오류: {spellcheck_response['errors_found']}개")
        
        return {
            'research': search_response,
            'story': final_story,
            'spellcheck': spellcheck_response,
            'cost': story_response['cost']
        }

# 사용 예시
writer = ComprehensiveWriter(client)
result = await writer.research_and_write("마법학교", "판타지")
print("\n=== 최종 작품 ===")
print(result['story'])
```

### 2. Google Docs 기반 협업 도구
```javascript
// Google Docs 협업 창작 도구
class CollaborativeWriter {
  constructor(client) {
    this.client = client;
    this.documentId = null;
  }

  async createProject(title, initialIdea) {
    // 1. 새 문서 생성
    const docResponse = await this.client.request('/api/docs/create', {
      method: 'POST',
      body: JSON.stringify({
        title: title,
        content: `프로젝트: ${title}\n\n초기 아이디어: ${initialIdea}\n\n`
      })
    });

    this.documentId = docResponse.document_id;
    console.log(`프로젝트 문서 생성: ${docResponse.document_url}`);

    // 2. 아이디어 확장을 위한 웹 검색
    const searchResponse = await this.client.request('/api/web-search', {
      method: 'POST',
      body: JSON.stringify({
        query: initialIdea,
        source: 'web',
        num_results: 5,
        include_summary: true
      })
    });

    // 3. 검색 결과를 문서에 추가
    const researchSection = `\n\n=== 리서치 자료 ===\n${searchResponse.summary}\n\n`;
    
    await this.client.request(`/api/docs/${this.documentId}`, {
      method: 'PUT',
      body: JSON.stringify({
        content: docResponse.content + researchSection
      })
    });

    return {
      documentId: this.documentId,
      documentUrl: docResponse.document_url,
      research: searchResponse
    };
  }

  async generateChapter(chapterTitle, prompt) {
    // 1. 현재 문서 내용 가져오기
    const docResponse = await this.client.request(`/api/docs/${this.documentId}`);
    
    // 2. 문서 기반 스토리 생성
    const storyResponse = await this.client.request('/api/docs/generate-story', {
      method: 'POST',
      body: JSON.stringify({
        document_id: this.documentId,
        prompt: `${chapterTitle}: ${prompt}`,
        max_tokens: 3000
      })
    });

    // 3. 맞춤법 검사
    const spellcheckResponse = await this.client.request('/api/spellcheck', {
      method: 'POST',
      body: JSON.stringify({
        text: storyResponse.generated_story,
        auto_correct: true
      })
    });

    // 4. 새 챕터를 문서에 추가
    const newChapter = `\n\n=== ${chapterTitle} ===\n${spellcheckResponse.corrected_text}\n`;
    const updatedContent = docResponse.content + newChapter;

    await this.client.request(`/api/docs/${this.documentId}`, {
      method: 'PUT',
      body: JSON.stringify({
        content: updatedContent
      })
    });

    console.log(`챕터 '${chapterTitle}' 추가 완료`);
    console.log(`정확도: ${spellcheckResponse.accuracy}%`);

    return {
      chapter: spellcheckResponse.corrected_text,
      accuracy: spellcheckResponse.accuracy,
      cost: storyResponse.cost
    };
  }

  async analyzeProject() {
    return await this.client.request('/api/docs/analyze', {
      method: 'POST',
      body: JSON.stringify({
        document_id: this.documentId
      })
    });
  }
}

// 사용 예시
const collaborativeWriter = new CollaborativeWriter(client);

// 프로젝트 시작
const project = await collaborativeWriter.createProject(
  "마법사의 모험",
  "중세 시대 마법사가 용을 물리치는 이야기"
);

// 챕터들 생성
await collaborativeWriter.generateChapter("1장: 마법사의 등장", "주인공 마법사를 소개하고 모험의 시작을 그려줘");
await collaborativeWriter.generateChapter("2장: 용의 위협", "마을을 위협하는 용에 대한 이야기를 써줘");
await collaborativeWriter.generateChapter("3장: 최종 결전", "마법사와 용의 최종 대결을 그려줘");

// 프로젝트 분석
const analysis = await collaborativeWriter.analyzeProject();
console.log("프로젝트 분석 결과:", analysis);
```

## ⚠️ 에러 처리

### 1. 포괄적인 에러 처리
```python
# 강력한 에러 처리를 포함한 API 클라이언트
import time
from typing import Optional

class RobustLoopAIClient:
    def __init__(self, base_url: str = "http://localhost:8080", max_retries: int = 3):
        self.base_url = base_url
        self.max_retries = max_retries
        self.session = requests.Session()
    
    def request_with_retry(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """재시도 로직이 포함된 요청"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method, 
                    f"{self.base_url}{endpoint}", 
                    timeout=30,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                print(f"시도 {attempt + 1}: 타임아웃 발생")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 지수적 백오프
                    
            except requests.exceptions.ConnectionError:
                print(f"시도 {attempt + 1}: 연결 오류")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code >= 500:
                    print(f"시도 {attempt + 1}: 서버 오류 ({e.response.status_code})")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                else:
                    # 클라이언트 오류는 재시도하지 않음
                    print(f"클라이언트 오류: {e.response.status_code}")
                    try:
                        error_detail = e.response.json()
                        print(f"오류 세부사항: {error_detail}")
                    except:
                        print(f"응답 내용: {e.response.text}")
                    return None
                    
            except Exception as e:
                print(f"예상치 못한 오류: {e}")
                return None
        
        print(f"최대 재시도 횟수 ({self.max_retries})를 초과했습니다")
        return None

# 사용 예시
robust_client = RobustLoopAIClient()

# 안전한 API 호출
result = robust_client.request_with_retry('POST', '/api/chat', json={
    'message': '안전한 요청 테스트',
    'history': [],
    'maxTokens': 1000,
    'isLongForm': False,
    'continueStory': False
})

if result:
    print("요청 성공:", result['response'])
else:
    print("요청 실패")
```

### 2. 실시간 상태 모니터링
```javascript
// 서버 상태 모니터링 클래스
class ServerMonitor {
  constructor(client, checkInterval = 30000) {
    this.client = client;
    this.checkInterval = checkInterval;
    this.isMonitoring = false;
    this.listeners = [];
  }

  async checkHealth() {
    try {
      const response = await this.client.request('/api/health');
      return {
        status: 'online',
        timestamp: response.timestamp,
        openai_initialized: response.openai_client_initialized,
        chat_initialized: response.chat_handler_initialized
      };
    } catch (error) {
      return {
        status: 'offline',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  async getCostStatus() {
    try {
      return await this.client.request('/api/cost-status');
    } catch (error) {
      console.error('비용 상태 조회 실패:', error);
      return null;
    }
  }

  startMonitoring() {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    console.log('서버 모니터링 시작');

    const monitor = async () => {
      const health = await this.checkHealth();
      const cost = await this.getCostStatus();
      
      const status = {
        ...health,
        cost_info: cost
      };

      // 리스너들에게 상태 전달
      this.listeners.forEach(listener => listener(status));

      if (this.isMonitoring) {
        setTimeout(monitor, this.checkInterval);
      }
    };

    monitor();
  }

  stopMonitoring() {
    this.isMonitoring = false;
    console.log('서버 모니터링 중지');
  }

  addListener(callback) {
    this.listeners.push(callback);
  }

  removeListener(callback) {
    const index = this.listeners.indexOf(callback);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }
}

// 사용 예시
const monitor = new ServerMonitor(client);

monitor.addListener((status) => {
  console.log(`서버 상태: ${status.status}`);
  if (status.cost_info) {
    console.log(`비용: $${status.cost_info.current_cost}/${status.cost_info.monthly_budget}`);
  }
  
  if (status.status === 'offline') {
    console.error('서버 오프라인! 재연결 시도 중...');
  }
});

monitor.startMonitoring();

// 5분 후 모니터링 중지
setTimeout(() => {
  monitor.stopMonitoring();
}, 300000);
```

---

이 예제들은 Loop AI API의 모든 기능을 실제 상황에서 활용하는 방법을 보여줍니다. 각 예제는 독립적으로 실행할 수 있으며, 필요에 따라 조합하여 더 복잡한 애플리케이션을 구축할 수 있습니다.

**관련 문서**:
- [API 메인 문서](./README.md)
- [웹 검색 API 상세 가이드](./web-search-api.md)
- [문제 해결 가이드](./troubleshooting.md)