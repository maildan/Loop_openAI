# Fantasy Name Generator API

이세계 판타지 캐릭터 이름 생성을 위한 고급 API입니다. 애니메이션 스타일부터 서양 판타지까지 다양한 스타일의 이름을 생성할 수 있습니다.

## 📋 목차
- [개요](#개요)
- [지원 스타일](#지원-스타일)
- [API 엔드포인트](#api-엔드포인트)
- [데이터 모델](#데이터-모델)
- [사용 예제](#사용-예제)
- [고급 기능](#고급-기능)

## 🎯 개요

Fantasy Name Generator API는 다음과 같은 기능을 제공합니다:

- **다양한 스타일**: 이세계 애니메이션, 서양 판타지, 조합형 생성
- **성별 지원**: 남성/여성/혼합 옵션
- **직업 기반**: 마법사, 기사, 도적, 성직자, 용사별 특화 이름
- **원소 속성**: 불, 물, 땅, 바람, 빛, 어둠 기반 이름
- **배치 생성**: 카테고리별 대량 생성 기능

## 🎨 지원 스타일

### 1. 이세계 애니메이션 스타일 (`anime`)
인기 이세계 애니메이션과 라이트노벨의 캐릭터 이름 스타일을 재현합니다.

**여성 캐릭터 예시:**
- 에밀리아, 렘, 람, 베아트리체
- 카구야, 치카, 하야사카
- 레지나, 셀레스티아, 루나

**남성 캐릭터 예시:**
- 키리토, 아스나, 클라인
- 림루, 베니마루, 소우에이
- 그레이라트, 루데우스

### 2. 서양 판타지 스타일 (`western`)
클래식 서양 판타지 소설과 RPG의 전통적인 이름들입니다.

**예시:**
- 갈라드리엘, 아라곤, 레골라스
- 허마이오니, 론, 해리
- 간달프, 사루만, 라다가스트

### 3. 조합형 스타일 (`composed`)
기존 이름의 음절을 조합하여 새롭고 창의적인 이름을 생성합니다.

**생성 규칙:**
- 접두사 + 중간 음절 + 접미사 조합
- 성별에 따른 어미 자동 조정
- 발음하기 쉬운 조합 우선 선택

## 📡 API 엔드포인트

### 1. 개별 이름 생성

#### `POST /api/names/generate`

단일 또는 복수의 이름을 생성합니다.

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `gender` | string | No | "female" | 성별 (male, female) |
| `style` | string | No | "anime" | 스타일 (anime, western, composed, mixed) |
| `character_class` | string | No | null | 캐릭터 클래스 (마법사, 기사, 도적, 성직자, 용사) |
| `element` | string | No | null | 원소 속성 (fire, water, earth, air, light, dark) |
| `count` | integer | No | 1 | 생성할 이름 개수 (1-20) |

**요청 예시:**
```json
{
  "gender": "female",
  "style": "anime",
  "character_class": "마법사",
  "element": "fire",
  "count": 5
}
```

**응답 형식:**
```json
{
  "names": [
    {
      "name": "이그니아",
      "gender": "female",
      "type": "마법사",
      "style": "elemental",
      "class": "마법사",
      "element": "fire"
    }
  ],
  "request_params": {
    "gender": "female",
    "style": "anime",
    "character_class": "마법사",
    "element": "fire",
    "count": 5
  },
  "total_generated": 5
}
```

### 2. 배치 생성

#### `POST /api/names/batch`

카테고리별로 이름을 대량 생성합니다.

**요청 파라미터:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `count_per_category` | integer | No | 5 | 카테고리별 생성 개수 (1-10) |

**요청 예시:**
```json
{
  "count_per_category": 3
}
```

**응답 형식:**
```json
{
  "categories": {
    "isekai_heroines": [
      {
        "name": "에밀리아",
        "type": "이세계 히로인",
        "origin": "애니메이션 스타일"
      }
    ],
    "isekai_heroes": [
      {
        "name": "키리토",
        "type": "이세계 주인공", 
        "origin": "라이트노벨 스타일"
      }
    ],
    "fantasy_princesses": [
      {
        "name": "갈라드리엘 펜드래곤",
        "type": "판타지 공주",
        "origin": "서양 판타지"
      }
    ],
    "fantasy_knights": [
      {
        "name": "아서",
        "type": "판타지 기사",
        "origin": "기사 클래스"
      }
    ],
    "elemental_mages": [
      {
        "name": "이그니스",
        "type": "fire 마법사",
        "origin": "원소 마법"
      }
    ],
    "noble_families": [
      {
        "family_name": "그레이라트",
        "lord": "루데우스 그레이라트",
        "lady": "실피에트 그레이라트",
        "type": "귀족 가문"
      }
    ]
  },
  "total_generated": 18
}
```

### 3. 캐릭터 클래스 목록

#### `GET /api/names/classes`

사용 가능한 캐릭터 클래스 목록을 반환합니다.

**응답 형식:**
```json
{
  "classes": [
    {
      "id": "마법사",
      "name": "마법사",
      "description": "마법을 다루는 학자형 캐릭터",
      "icon": "🧙‍♀️",
      "typical_names": ["메를린", "간달프", "제니스"]
    },
    {
      "id": "기사",
      "name": "기사",
      "description": "검과 방패로 정의를 수호하는 전사",
      "icon": "⚔️",
      "typical_names": ["아서", "랜슬롯", "갈라하드"]
    }
  ]
}
```

### 4. 원소 속성 목록

#### `GET /api/names/elements`

사용 가능한 원소 속성 목록을 반환합니다.

**응답 형식:**
```json
{
  "elements": [
    {
      "id": "fire",
      "name": "불",
      "description": "열정과 파괴의 힘",
      "icon": "🔥",
      "color": "#ff4444",
      "typical_names": ["이그니스", "플레임", "솔라"]
    },
    {
      "id": "water", 
      "name": "물",
      "description": "치유와 정화의 힘",
      "icon": "💧",
      "color": "#4444ff",
      "typical_names": ["아쿠아", "플루비아", "마리나"]
    }
  ]
}
```

### 5. 예제 이름

#### `GET /api/names/examples`

각 카테고리별 샘플 이름들을 반환합니다.

**응답 형식:**
```json
{
  "examples": {
    "anime_heroines": [
      "에밀리아", "렘", "베아트리체", "카구야", "치카"
    ],
    "anime_heroes": [
      "키리토", "림루", "나츠키", "루데우스", "아인즈"
    ],
    "western_fantasy": [
      "갈라드리엘", "아라곤", "레골라스", "간달프", "사루만"
    ],
    "composed_names": [
      "세라피나", "엘리시아", "아리스토", "발데리안", "카스토르"
    ]
  }
}
```

## 📊 데이터 모델

### NameRequest
```typescript
interface NameRequest {
  gender?: "male" | "female";           // 성별
  style?: "anime" | "western" | "composed" | "mixed"; // 스타일
  character_class?: string;             // 캐릭터 클래스
  element?: "fire" | "water" | "earth" | "air" | "light" | "dark"; // 원소
  count?: number;                       // 생성 개수 (1-20)
}
```

### GeneratedName
```typescript
interface GeneratedName {
  name: string;                         // 생성된 이름
  gender: "male" | "female";           // 성별
  type: string;                         // 타입 설명
  style: string;                        // 사용된 스타일
  class?: string;                       // 캐릭터 클래스
  element?: string;                     // 원소 속성
}
```

### BatchNameRequest
```typescript
interface BatchNameRequest {
  count_per_category?: number;          // 카테고리별 생성 개수 (1-10)
}
```

## 💡 사용 예제

### 기본 이름 생성
```bash
curl -X POST "http://localhost:8000/api/names/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "female",
    "style": "anime",
    "count": 3
  }'
```

### 클래스 기반 이름 생성
```bash
curl -X POST "http://localhost:8000/api/names/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "male",
    "character_class": "기사",
    "count": 5
  }'
```

### 원소 마법사 이름 생성
```bash
curl -X POST "http://localhost:8000/api/names/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "female",
    "element": "water",
    "character_class": "마법사",
    "count": 3
  }'
```

### JavaScript 예제
```javascript
async function generateFantasyNames() {
  try {
    const response = await fetch('http://localhost:8000/api/names/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        gender: 'female',
        style: 'anime',
        character_class: '마법사',
        element: 'fire',
        count: 5
      })
    });

    const data = await response.json();
    
    data.names.forEach(character => {
      console.log(`${character.name} - ${character.type}`);
    });
  } catch (error) {
    console.error('이름 생성 실패:', error);
  }
}
```

### Python 예제
```python
import requests
import json

def generate_batch_names():
    url = "http://localhost:8000/api/names/batch"
    payload = {"count_per_category": 3}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        
        for category, names in data['categories'].items():
            print(f"\n{category}:")
            for item in names:
                if 'family_name' in item:
                    print(f"  🏰 {item['family_name']} 가문")
                    print(f"     👑 {item['lord']}")
                    print(f"     👸 {item['lady']}")
                else:
                    print(f"  ✨ {item['name']} ({item['type']})")
    else:
        print(f"에러: {response.status_code}")
```

## 🚀 고급 기능

### 1. 조합형 이름 생성 알고리즘

조합형 스타일은 다음과 같은 규칙으로 작동합니다:

1. **음절 데이터베이스**: 기존 인기 캐릭터 이름들을 분석하여 음절별로 분류
2. **조합 규칙**: 접두사 + 중간음절 + 접미사의 3단계 조합
3. **성별 적응**: 생성된 이름의 어미를 성별에 맞게 자동 조정
4. **발음 최적화**: 발음하기 어려운 조합을 필터링

### 2. 클래스별 특화 생성

각 캐릭터 클래스는 고유한 이름 패턴을 가집니다:

- **마법사**: 라틴어 기반, 신비로운 음향
- **기사**: 강인하고 권위 있는 소리
- **도적**: 날렵하고 기민한 느낌
- **성직자**: 성스럽고 온화한 분위기
- **용사**: 영웅적이고 웅장한 느낌

### 3. 원소 기반 네이밍

원소별로 특화된 이름 생성:

- **불**: 열정, 에너지, 파괴적 힘을 표현
- **물**: 흐름, 치유, 정화를 의미
- **땅**: 안정성, 견고함, 자연을 나타냄  
- **바람**: 자유, 속도, 변화를 상징
- **빛**: 희망, 순수, 신성함을 표현
- **어둠**: 신비, 깊이, 미지를 의미

### 4. 문화적 고려사항

이름 생성 시 다음 요소들을 고려합니다:

- **일본 애니메이션 문화**: 이세계 장르의 네이밍 트렌드
- **서양 판타지 전통**: 톨킨, C.S. 루이스 등의 명명 규칙
- **언어학적 조화**: 발음의 자연스러움과 기억하기 쉬운 패턴
- **성별 구분**: 각 언어권의 성별 구분 관습 반영

## ⚠️ 제한사항 및 주의사항

1. **생성 제한**: 한 번에 최대 20개까지 생성 가능
2. **배치 제한**: 카테고리별 최대 10개까지 생성 가능  
3. **중복 가능성**: 인기 이름의 경우 중복 생성될 수 있음
4. **문화적 민감성**: 특정 문화권의 실제 이름과 유사할 수 있음
5. **저작권**: 기존 작품의 캐릭터명과 유사할 수 있음

## 🔧 문제 해결

### 자주 발생하는 문제

**Q: 같은 이름이 반복 생성됩니다**
A: `style`을 "mixed"로 설정하거나 `character_class`와 `element`를 조합하여 더 다양한 이름을 생성할 수 있습니다.

**Q: 원하는 스타일의 이름이 나오지 않습니다**
A: `style` 파라미터를 명시적으로 지정하고, 예제 목록을 참고하여 적절한 조합을 찾아보세요.

**Q: 성별이 맞지 않는 이름이 생성됩니다**
A: 조합형 생성의 경우 알고리즘이 자동 조정하지만, 완벽하지 않을 수 있습니다. 다시 생성해보거나 다른 스타일을 시도해보세요.

---

**관련 문서:**
- [메인 API 문서](./README.md)
- [Story Generator API](./story-generator.md)
- [사용 예제](./examples.md) 