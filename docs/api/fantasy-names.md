# 판타지 이름 생성 API

Loop AI의 판타지 이름 생성 API를 사용하여 다양한 스타일의 이름을 생성할 수 있습니다. 이 API는 이세계 애니메이션, 서양 판타지, 조합형 이름, 캐릭터 클래스별, 원소/속성별 이름 등을 지원합니다.

## API 엔드포인트

### 1. 단일 이름 생성

```
POST /api/generate-name
```

#### 요청 파라미터

| 필드 | 타입 | 설명 | 기본값 |
|------|------|------|--------|
| style | string | 이름 스타일 (`isekai`, `western`, `composed`, `noble`) | `isekai` |
| gender | string | 성별 (`male`, `female`) | `female` |
| character_class | string | 캐릭터 클래스 (마법사, 기사, 도적 등) | `null` |
| element | string | 원소/속성 (불, 물, 바람, 대지, 빛, 어둠 등) | `null` |

#### 응답

```json
{
  "name": "에밀리아"
}
```

### 2. 다중 이름 생성

```
POST /api/generate-multiple-names
```

#### 요청 파라미터

| 필드 | 타입 | 설명 | 기본값 |
|------|------|------|--------|
| count | integer | 생성할 이름 개수 (1-50) | 10 |
| gender | string | 성별 (`male`, `female`) | `female` |
| style | string | 이름 스타일 (`mixed`, `isekai`, `western`, `composed`, `class`, `elemental`, `noble`) | `mixed` |

#### 응답

```json
{
  "names": [
    {
      "name": "알베도",
      "gender": "female",
      "style": "isekai",
      "character_class": "미정",
      "element": "미정",
      "personality": "신비로운"
    },
      {
      "name": "갈라드리엘",
      "gender": "female",
      "style": "western",
      "character_class": "미정",
      "element": "미정",
      "personality": "우아한"
    }
    // ... 추가 이름들
  ]
}
```

### 3. 카테고리별 배치 이름 생성

```
POST /api/batch-generate-names
```

#### 요청 파라미터

| 필드 | 타입 | 설명 | 기본값 |
|------|------|------|--------|
| count_per_category | integer | 카테고리별 생성 개수 (1-20) | 5 |

#### 응답

```json
{
  "isekai_names": [
    {
      "name": "카구야",
      "type": "isekai",
      "origin": "anime-style"
    }
    // ... 추가 이름들
  ],
  "western_fantasy_names": [
    {
      "name": "아르웬",
      "type": "western",
      "origin": "fantasy-classic"
    }
    // ... 추가 이름들
  ],
  "noble_families": [
    {
      "family_name": "펜드래곤",
      "lord": "아서",
      "lady": "모르가나",
      "type": "noble"
    }
    // ... 추가 가문들
  ]
}
```

## 지원되는 스타일

- `isekai`: 이세계 애니메이션 스타일 이름 (에밀리아, 카구야, 림루 등)
- `western`: 서양 판타지 스타일 이름 (갈라드리엘, 아라곤, 허마이오니 등)
- `composed`: 음절 조합으로 생성된 이름
- `noble`: 귀족/가문 이름 (이름 + 성)
- `mixed`: 다양한 스타일 혼합 (다중 이름 생성시에만 사용 가능)

## 지원되는 캐릭터 클래스

마법사, 기사, 도적, 성직자, 용사, 전사, 궁수, 소환사, 용기사, 암살자, 광전사, 정령사, 주술사, 연금술사, 음유시인, 무희 등

## 지원되는 원소/속성

불(fire), 물(water), 바람(air), 대지(earth), 빛(light), 어둠(dark), 번개(lightning), 얼음(ice), 강철(steel), 자연(nature) 등

## 사용 예제

### 단일 이름 생성

```bash
curl -X POST http://localhost:8000/api/generate-name \
  -H "Content-Type: application/json" \
  -d '{"style": "isekai", "gender": "female"}'
```

### 다중 이름 생성

```bash
curl -X POST http://localhost:8000/api/generate-multiple-names \
  -H "Content-Type: application/json" \
  -d '{"count": 5, "gender": "male", "style": "mixed"}'
```

### 카테고리별 배치 이름 생성

```bash
curl -X POST http://localhost:8000/api/batch-generate-names \
  -H "Content-Type: application/json" \
  -d '{"count_per_category": 3}'
``` 