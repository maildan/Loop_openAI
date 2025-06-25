# Story Generator API

Qwen2.5 기반 한국어 창작 AI API입니다. 다양한 장르의 고품질 소설과 스토리를 생성할 수 있습니다.

## 📋 목차
- [개요](#개요)
- [지원 장르](#지원-장르)
- [API 엔드포인트](#api-엔드포인트)
- [고급 설정](#고급-설정)
- [사용 예제](#사용-예제)
- [베스트 프랙티스](#베스트-프랙티스)

## 🎯 개요

Story Generator API는 다음과 같은 기능을 제공합니다:

- **다양한 장르**: 판타지, 로맨스, SF, 미스터리, 드라마 지원
- **한국어 특화**: 자연스러운 한국어 문체와 표현
- **세밀한 제어**: 온도, 토큰 수, 반복 방지 등 고급 설정
- **프롬프트 최적화**: 장르별 최적화된 프롬프트 템플릿
- **응급처치 시스템**: Catastrophic Forgetting 방지 기술

## 📚 지원 장르

### 1. 판타지 (`fantasy`)
마법과 모험이 가득한 환상적인 세계의 이야기

**특징:**
- 마법 시스템과 판타지 생물
- 영웅의 여정과 모험 서사
- 선악 구도와 운명적 만남

**예시 프롬프트:**
- "용과 마법사의 모험 이야기를 써줘"
- "마법학교에서 일어나는 미스터리"
- "전설의 검을 찾아 떠나는 여행"

### 2. 로맨스 (`romance`)
달콤하고 감동적인 사랑 이야기

**특징:**
- 감정적 깊이와 심리 묘사
- 로맨틱한 상황과 갈등
- 해피엔딩과 성장 서사

**예시 프롬프트:**
- "운명적인 만남에서 시작되는 사랑 이야기"
- "소꿉친구에서 연인으로 발전하는 과정"
- "시간을 넘나드는 로맨스"

### 3. SF (`sf`)
미래와 과학기술이 중심인 공상과학 이야기

**특징:**
- 첨단 기술과 미래 사회
- 과학적 개념과 상상력
- 인간성에 대한 탐구

**예시 프롬프트:**
- "인공지능과 인간의 우정"
- "화성 식민지에서 벌어지는 사건"
- "시간여행으로 인한 패러독스"

### 4. 미스터리 (`mystery`)
수수께끼와 추리가 핵심인 이야기

**특징:**
- 논리적 추론과 단서 탐색
- 서스펜스와 긴장감
- 예상치 못한 반전

**예시 프롬프트:**
- "밀실에서 벌어진 불가능한 살인사건"
- "사라진 고고학자의 비밀"
- "과거와 현재를 잇는 연쇄 사건"

### 5. 드라마 (`drama`)
인간의 감정과 관계를 다룬 현실적인 이야기

**특징:**
- 일상적 갈등과 성장
- 인간관계의 복잡성
- 현실적 문제 해결

**예시 프롬프트:**
- "가족 간의 화해를 그린 이야기"
- "꿈을 위해 고군분투하는 청춘"
- "세대 간 이해와 소통"

## 📡 API 엔드포인트

### 1. 스토리 생성

#### `POST /api/generate`

프롬프트를 기반으로 스토리를 생성합니다.

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `prompt` | string | Yes | - | 스토리 생성을 위한 프롬프트 |
| `genre` | string | No | "fantasy" | 장르 (fantasy, romance, sf, mystery, drama) |
| `length` | integer | No | 200 | 생성할 텍스트 길이 (단어 수) |
| `temperature` | float | No | 0.7 | 창의성 제어 (0.1-1.0) |
| `max_new_tokens` | integer | No | 512 | 최대 토큰 수 (100-1000) |

**요청 예시:**
```json
{
  "prompt": "마법학교에서 일어나는 신비한 사건을 그린 이야기를 써줘",
  "genre": "fantasy",
  "temperature": 0.8,
  "max_new_tokens": 400
}
```

**응답 형식:**
```json
{
  "generated_text": "호그와트와 같은 마법학교 '아르카나 아카데미아'에서 새 학기가 시작되었다. 첫 수업 날, 변신술 교실에서 이상한 일이 벌어졌다...",
  "genre": "fantasy",
  "prompt": "마법학교에서 일어나는 신비한 사건을 그린 이야기를 써줘",
  "metadata": {
    "model": "Qwen2.5-0.5B-Instruct",
    "temperature": 0.8,
    "max_new_tokens": 400,
    "actual_tokens": 387,
    "generation_time": 2.3,
    "korean_filter_applied": true,
    "emergency_fix_applied": true
  }
}
```

### 2. 장르 목록

#### `GET /api/genres`

사용 가능한 장르 목록을 반환합니다.

**응답 형식:**
```json
{
  "genres": [
    {
      "value": "fantasy",
      "label": "판타지",
      "description": "마법과 모험이 가득한 환상적인 세계",
      "icon": "🧙‍♂️",
      "color": "#8B5CF6",
      "keywords": ["마법", "모험", "용", "기사", "마법사"]
    },
    {
      "value": "romance",
      "label": "로맨스", 
      "description": "달콤하고 감동적인 사랑 이야기",
      "icon": "💕",
      "color": "#EC4899",
      "keywords": ["사랑", "연인", "감정", "만남", "이별"]
    },
    {
      "value": "sf",
      "label": "SF",
      "description": "미래와 과학기술이 중심인 공상과학",
      "icon": "🚀",
      "color": "#06B6D4", 
      "keywords": ["미래", "로봇", "우주", "기술", "AI"]
    },
    {
      "value": "mystery",
      "label": "미스터리",
      "description": "수수께끼와 추리가 핵심인 이야기",
      "icon": "🔍",
      "color": "#64748B",
      "keywords": ["추리", "사건", "단서", "범인", "비밀"]
    },
    {
      "value": "drama",
      "label": "드라마",
      "description": "인간의 감정과 관계를 다룬 현실적인 이야기",
      "icon": "🎭",
      "color": "#F59E0B",
      "keywords": ["가족", "성장", "갈등", "일상", "인간관계"]
    }
  ]
}
```

### 3. 예시 프롬프트

#### `GET /api/examples`

각 장르별 예시 프롬프트를 반환합니다.

**응답 형식:**
```json
{
  "examples": [
    {
      "prompt": "용과 마법사의 모험 이야기를 써달라고 병신아",
      "genre": "fantasy",
      "description": "클래식 판타지 모험담",
      "difficulty": "beginner",
      "expected_length": "medium"
    },
    {
      "prompt": "시간을 넘나드는 로맨스를 그려줘",
      "genre": "romance", 
      "description": "시간여행 로맨스",
      "difficulty": "intermediate",
      "expected_length": "long"
    },
    {
      "prompt": "AI와 인간의 우정을 다룬 SF 소설",
      "genre": "sf",
      "description": "AI와 인간성 탐구",
      "difficulty": "advanced",
      "expected_length": "medium"
    }
  ]
}
```

## 📊 데이터 모델

### StoryRequest
```typescript
interface StoryRequest {
  prompt: string;                       // 필수: 스토리 프롬프트
  genre?: "fantasy" | "romance" | "sf" | "mystery" | "drama"; // 장르
  length?: number;                      // 텍스트 길이 (단어 수)
  temperature?: number;                 // 창의성 (0.1-1.0)
  max_new_tokens?: number;             // 최대 토큰 수 (100-1000)
}
```

### StoryResponse
```typescript
interface StoryResponse {
  generated_text: string;              // 생성된 스토리
  genre: string;                       // 사용된 장르
  prompt: string;                      // 원본 프롬프트
  metadata: {
    model: string;                     // 사용된 모델명
    temperature: number;               // 적용된 온도
    max_new_tokens: number;           // 최대 토큰 수
    actual_tokens: number;            // 실제 생성된 토큰 수
    generation_time: number;          // 생성 시간 (초)
    korean_filter_applied: boolean;   // 한국어 필터 적용 여부
    emergency_fix_applied: boolean;   // 응급처치 적용 여부
  };
}
```

## ⚙️ 고급 설정

### 온도 (Temperature) 설정

온도는 생성되는 텍스트의 창의성과 일관성을 조절합니다:

| 온도 | 특성 | 권장 용도 |
|------|------|-----------|
| 0.1-0.3 | 매우 일관적, 예측 가능 | 기술 문서, 정확한 정보 전달 |
| 0.4-0.6 | 균형잡힌 창의성 | 일반적인 스토리, 소설 |
| 0.7-0.8 | 창의적, 다양한 표현 | 판타지, SF, 실험적 글쓰기 |
| 0.9-1.0 | 매우 창의적, 예측 불가 | 추상적 작품, 예술적 표현 |

### 토큰 길이 설정

| 토큰 수 | 예상 길이 | 권장 용도 |
|---------|-----------|-----------|
| 100-200 | 짧은 단편 (2-3 문단) | 아이디어 스케치, 개요 |
| 300-500 | 중간 길이 (1-2 페이지) | 단편 소설, 에피소드 |
| 600-800 | 긴 이야기 (3-4 페이지) | 중편 소설, 상세한 묘사 |
| 900-1000 | 매우 긴 이야기 (5+ 페이지) | 장편 소설 일부 |

### 장르별 최적 설정

```json
{
  "fantasy": {
    "temperature": 0.8,
    "max_new_tokens": 600,
    "focus": "adventure, magic, world-building"
  },
  "romance": {
    "temperature": 0.7,
    "max_new_tokens": 500,
    "focus": "emotions, character development"
  },
  "sf": {
    "temperature": 0.6,
    "max_new_tokens": 700,
    "focus": "technology, logic, concepts"
  },
  "mystery": {
    "temperature": 0.5,
    "max_new_tokens": 600,
    "focus": "clues, suspense, logic"
  },
  "drama": {
    "temperature": 0.6,
    "max_new_tokens": 400,
    "focus": "realism, emotions, dialogue"
  }
}
```

## 💡 사용 예제

### 기본 스토리 생성
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "마법학교 신입생의 첫날 이야기",
    "genre": "fantasy"
  }'
```

### 고급 설정으로 생성
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "시간여행으로 과거에 간 과학자의 딜레마",
    "genre": "sf",
    "temperature": 0.8,
    "max_new_tokens": 800
  }'
```

### JavaScript 예제
```javascript
async function generateStory() {
  try {
    const response = await fetch('http://localhost:8000/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: '첫사랑과의 재회를 그린 감동적인 이야기',
        genre: 'romance',
        temperature: 0.7,
        max_new_tokens: 600
      })
    });

    const story = await response.json();
    
    console.log('Generated Story:');
    console.log(story.generated_text);
    console.log(`\nMetadata: ${story.metadata.actual_tokens} tokens in ${story.metadata.generation_time}s`);
    
  } catch (error) {
    console.error('스토리 생성 실패:', error);
  }
}
```

### Python 예제
```python
import requests
import json

def generate_mystery_story():
    url = "http://localhost:8000/api/generate"
    
    payload = {
        "prompt": "도서관에서 발견된 고대 책의 비밀",
        "genre": "mystery",
        "temperature": 0.6,
        "max_new_tokens": 500
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        story = response.json()
        
        print("🔍 Generated Mystery Story:")
        print("=" * 50)
        print(story['generated_text'])
        print("=" * 50)
        print(f"Genre: {story['genre']}")
        print(f"Tokens: {story['metadata']['actual_tokens']}")
        print(f"Time: {story['metadata']['generation_time']:.2f}s")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# 실행
generate_mystery_story()
```

## 🎯 베스트 프랙티스

### 1. 효과적인 프롬프트 작성

**좋은 프롬프트:**
```
"마법학교 3학년 학생이 금지된 도서관에서 발견한 고대 마법서로 인해 벌어지는 모험을 그려줘. 주인공은 호기심 많지만 조금 겁이 많은 성격이야."
```

**피해야 할 프롬프트:**
```
"재미있는 이야기 써줘"  // 너무 모호함
"소설"                // 구체적인 요청 없음
```

### 2. 장르별 프롬프트 팁

**판타지:**
- 구체적인 마법 시스템이나 세계관 언급
- 주인공의 목표와 장애물 명시
- 판타지 요소(용, 마법사, 왕국 등) 포함

**로맨스:**
- 주인공들의 관계와 배경 설명
- 감정적 상황이나 갈등 상황 제시
- 로맨틱한 설정이나 상황 구체화

**SF:**
- 과학적 개념이나 미래 기술 언급
- 시간적 배경(미래, 현재, 과거) 명시
- 과학적 문제나 딜레마 제시

### 3. 최적의 파라미터 설정

**창의적 글쓰기:** temperature 0.7-0.8
**일관된 서사:** temperature 0.5-0.6  
**실험적 표현:** temperature 0.8-1.0

**단편:** max_new_tokens 300-500
**중편:** max_new_tokens 500-700
**장편 일부:** max_new_tokens 700-1000

### 4. 연속 생성 기법

긴 이야기를 생성할 때는 여러 번에 걸쳐 생성하고 이어붙이는 것이 효과적입니다:

```javascript
async function generateLongStory(initialPrompt, chapters = 3) {
  let fullStory = "";
  let currentPrompt = initialPrompt;
  
  for (let i = 0; i < chapters; i++) {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: currentPrompt,
        genre: 'fantasy',
        max_new_tokens: 400
      })
    });
    
    const chapter = await response.json();
    fullStory += chapter.generated_text + "\n\n";
    
    // 다음 챕터를 위한 프롬프트 준비
    currentPrompt = `이전 이야기: ${chapter.generated_text.slice(-200)}\n\n이어서 다음 장면을 써줘:`;
  }
  
  return fullStory;
}
```

## ⚠️ 제한사항 및 주의사항

1. **토큰 제한**: 최대 1000 토큰까지 생성 가능
2. **생성 시간**: 모델 크기에 따라 2-10초 소요
3. **한국어 우선**: 한국어 출력에 최적화됨
4. **내용 필터링**: 부적절한 콘텐츠는 자동 필터링
5. **일관성**: 매우 긴 텍스트에서는 일관성이 떨어질 수 있음

## 🔧 문제 해결

### 자주 발생하는 문제

**Q: 생성된 텍스트가 너무 짧습니다**
A: `max_new_tokens` 값을 늘리고 `temperature`를 0.7 이상으로 설정해보세요.

**Q: 내용이 반복적입니다**
A: `temperature`를 높이거나 더 구체적인 프롬프트를 제공해보세요.

**Q: 장르에 맞지 않는 내용이 생성됩니다**
A: 프롬프트에 장르 특성을 명시적으로 언급하고, 적절한 `genre` 파라미터를 설정하세요.

**Q: 생성 속도가 느립니다**
A: `max_new_tokens`를 줄이거나 여러 번에 나누어 생성하는 것을 고려해보세요.

### 응급처치 시스템

Loop AI는 Catastrophic Forgetting 문제를 해결하기 위한 응급처치 시스템을 포함합니다:

- **자동 프롬프트 강화**: 원본 프롬프트를 한국어 창작에 최적화
- **파라미터 조정**: 안정적인 생성을 위한 최적 파라미터 적용
- **품질 보장**: 한국어 필터와 반복 방지 기능

---

**관련 문서:**
- [메인 API 문서](./README.md)
- [Fantasy Name Generator API](./fantasy-names.md)
- [사용 예제](./examples.md)
- [문제 해결](./troubleshooting.md) 