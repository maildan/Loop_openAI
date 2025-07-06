# Loop AI Story Generator & Assistant API

Loop AI의 핵심, 스토리 생성 및 AI 창작 지원 기능 API입니다. 작가의 창의적인 프로세스를 지원하기 위해 설계된 강력하고 다양한 엔드포인트를 제공합니다.

**API Base Path**: `/api/v1/story`

---

## 목차

1.  [API 철학](#api-철학)
2.  [엔드포인트 요약](#엔드포인트-요약)
3.  [공통 데이터 모델](#공통-데이터-모델)
4.  [API 상세 명세](#api-상세-명세)
    -   [스마트 문장 개선](#post-analyzesentence-improvement)
    -   [실시간 플롯 홀 감지](#post-analyzeplot-holes)
    -   [캐릭터 일관성 체크](#post-analyzecharacter-consistency)
    -   [AI 베타리더 종합 분석](#post-analyzebeta-read)
    -   [웹소설 트렌드 분석](#post-analyzetrends)
    -   [지능형 클리프행어 생성](#post-generatecliffhanger)
    -   [독자 반응 예측](#post-predictreader-response)
    -   [에피소드 길이 최적화](#post-optimizeepisode-length)

---

## API 철학

Loop AI의 Assistant API는 단순한 텍스트 생성을 넘어, 작가의 창작 과정에 깊숙이 관여하여 실질적인 도움을 주는 것을 목표로 합니다. 각 엔드포인트는 다음과 같은 원칙에 따라 설계되었습니다.

-   **모듈성 (Modularity)**: 각 기능은 독립적인 API로 분리되어 있어 필요한 기능만 선택적으로 사용할 수 있습니다.
-   **일관성 (Consistency)**: 모든 엔드포인트는 `/api/v1/story/{action-type}/{feature}` 형식의 일관된 경로를 따릅니다.
-   **명확성 (Clarity)**: 요청과 응답 모델은 명확하게 정의되어 있으며, 모든 필드는 구체적인 설명을 포함합니다.
-   **확장성 (Scalability)**: 새로운 AI 기능이 추가되더라도 기존 구조를 해치지 않고 쉽게 확장할 수 있습니다.

---

## 엔드포인트 요약

| Method | Endpoint                                        | 기능 요약                               |
| :----- | :---------------------------------------------- | :-------------------------------------- |
| `POST` | `/analyze/sentence-improvement`                 | 문장 개선안 제안                        |
| `POST` | `/analyze/plot-holes`                           | 플롯 홀 및 설정 오류 탐지               |
| `POST` | `/analyze/character-consistency`                | 캐릭터 설정과 실제 내용의 일관성 검증   |
| `POST` | `/analyze/beta-read`                            | 원고에 대한 종합적인 베타 리딩 리포트   |
| `POST` | `/analyze/trends`                               | 최신 웹소설 트렌드 분석 및 적용 제안    |
| `POST` | `/generate/cliffhanger`                         | 다음 화를 위한 클리프행어 자동 생성     |
| `POST` | `/predict/reader-response`                      | 특정 장면에 대한 독자 반응 예측         |
| `POST` | `/optimize/episode-length`                      | 플랫폼에 맞는 에피소드 분량 최적화      |

---

## 공통 데이터 모델

-   **`model`** (string, optional): 사용할 AI 모델을 지정합니다. (예: "gpt-4o", "gpt-4o-mini"). 지정하지 않으면 각 기능에 최적화된 기본 모델이 사용됩니다.
-   **`cost`** (float, response): 해당 API 호출에 소요된 비용 (USD).
-   **`tokens`** (integer, response): 해당 API 호출에 사용된 총 토큰 수.

---

## API 상세 명세

### `POST /analyze/sentence-improvement`

**스마트 문장 개선**: 단일 문장 또는 짧은 단락을 분석하여 문체, 리듬, 명확성 측면에서 여러 개선안을 제안합니다.

-   **Request Body**: `SmartSentenceImprovementRequest`
    ```json
    {
      "original_text": "기사가 매우 용감하게 앞으로 가서 용을 때렸다.",
      "model": "gpt-4o-mini"
    }
    ```
-   **Response Body**: `SmartSentenceImprovementResponse`
    ```json
    {
      "improvement_suggestions": "1. **\"기사는 용을 향해 용맹하게 돌진했다.\"**\n * **이유:** '돌진했다'는 표현이 '앞으로 갔다'보다 훨씬 더 역동적이고 긴박한 느낌을 줍니다...\n2. ...",
      "model": "gpt-4o-mini",
      "cost": 0.00012,
      "tokens": 800
    }
    ```

### `POST /analyze/plot-holes`

**실시간 플롯 홀 감지**: 이야기 전체 텍스트를 분석하여 플롯 홀, 설정 충돌 등을 감지합니다.

-   **Request Body**: `PlotHoleDetectionRequest`
    ```json
    {
      "full_story_text": "1화에서 철수는 17살이었다. ... 3화에서 철수는 갑자기 19살이 되어 수능을 봤다.",
      "model": "gpt-4o"
    }
    ```
-   **Response Body**: `PlotHoleDetectionResponse`
    ```json
    {
      "detection_report": "### 1. 캐릭터 설정 충돌\n- **문제점:** 1화에서 17세였던 주인공이 3화에서 갑자기 19세가 되었습니다...",
      "model": "gpt-4o",
      "cost": 0.0025,
      "tokens": 1500
    }
    ```

### `POST /analyze/character-consistency`

**캐릭터 일관성 체크**: 캐릭터 프로필과 실제 작품 내용을 비교하여 설정 붕괴를 감지합니다.

-   **Request Body**: `CharacterConsistencyRequest`
    ```json
    {
      "character_name": "이준호",
      "personality": "냉정하고 계산적임",
      "speech_style": "간결한 단답형",
      "core_values": "가문의 복수",
      "other_settings": "대기업의 유일한 후계자",
      "story_text_for_analysis": "...이준호는 그녀를 보자마자 사랑에 빠져 장황한 연설을 늘어놓았다..."
    }
    ```
-   **Response Body**: `CharacterConsistencyResponse`
    ```json
    {
      "consistency_report": "**[불일치 경고 🚨]**\n- **충돌 지점:** '냉정하고 계산적'이라는 성격 및 '간결한 단답형' 말투 설정과 달리...",
      "model": "gpt-4o",
      "cost": 0.0028,
      "tokens": 1800
    }
    ```

### `POST /analyze/beta-read`

**AI 베타리더 종합 분석**: 원고 전체를 다각도로 분석하여 종합적인 피드백 리포트를 제공합니다.

-   **Request Body**: `BetaReadRequest`
    ```json
    {
      "manuscript": "[...원고 전문...]",
      "genre": "회귀, 헌터",
      "target_audience": "20-30대 남성",
      "author_concerns": "주인공이 너무 강해서 재미없을까봐 걱정돼요."
    }
    ```
-   **Response Body**: `BetaReadResponse`
    ```json
    {
      "beta_read_report": { "executive_summary": "...", "pacing_and_flow": { "score": 90, ... } },
      "model": "gpt-4o",
      "cost": 0.015,
      "tokens": 8000
    }
    ```

### `POST /analyze/trends`

**웹소설 트렌드 분석**: 실시간 웹 검색을 통해 최신 트렌드를 분석하고, 작품에 적용할 아이디어를 제안합니다.

-   **Request Body**: `TrendAnalysisRequest`
    ```json
    {
      "genre": "회귀",
      "synopsis": "검사가 세상 멸망을 막기 위해 과거로 돌아가는 이야기",
      "keywords": ["회귀", "검사", "멸망"],
      "platform": "카카오페이지"
    }
    ```
-   **Response Body**: `TrendAnalysisResponse`
    ```json
    {
      "trend_report": "**최신 인기 트렌드 Top 3**\n1. 스트리밍/BJ 요소...",
      "model": "gpt-4o",
      "cost": 0.004,
      "tokens": 2500,
      "searched_data": [ { "title": "요즘 유행하는 웹소설 키워드", "url": "...", "snippet": "..." } ]
    }
    ```

### `POST /generate/cliffhanger`

**지능형 클리프행어 생성기**: 장르와 장면 맥락에 맞는 클리프행어 아이디어를 독자 반응 예측과 함께 제안합니다.

-   **Request Body**: `CliffhangerRequest`
    ```json
    {
      "genre": "로맨스 판타지",
      "scene_context": "남주인공이 여주인공에게 드디어 고백하고, 여주인공이 대답하려는 순간이다."
    }
    ```
-   **Response Body**: `CliffhangerResponse`
    ```json
    {
      "suggestions": [
        { "suggestion": "그 순간, 남주인공의 몸에 새겨진 저주의 문양이 검게 타오르기 시작했다.", "expected_reaction": "댓글 폭발 95% 예상..." }
      ],
      "model": "gpt-4o",
      "cost": 0.001,
      "tokens": 700
    }
    ```

### `POST /predict/reader-response`

**독자 반응 예측**: 특정 장면에 대한 플랫폼별 독자 반응(댓글, 이탈률 등)을 예측하고 개선안을 제안합니다.

-   **Request Body**: `ReaderResponseRequest`
    ```json
    {
      "platform": "네이버 시리즈",
      "scene_context": "주인공이 10년간의 헌신에도 불구하고 파티에서 배신당하고 쫓겨나는 장면."
    }
    ```
-   **Response Body**: `ReaderResponseResponse`
    ```json
    {
      "prediction_report": { "expected_comments": ["고구마 100개 먹은 기분", ...], "drop_off_risk": "30%", ... },
      "model": "gpt-4o",
      "cost": 0.003,
      "tokens": 2000
    }
    ```

### `POST /optimize/episode-length`

**에피소드 길이 최적화**: 플랫폼 특성에 맞춰 에피소드 분량 및 분할 지점을 최적화합니다.

-   **Request Body**: `EpisodeLengthRequest`
    ```json
    {
      "platform": "카카오페이지",
      "episode_text": "[...에피소드 전체 텍스트...]"
    }
    ```
-   **Response Body**: `EpisodeLengthResponse`
    ```json
    {
      "optimization_report": { "current_length": 7500, "target_length": 5500, "suggestions": ["불필요한 수식어 제거...", "A와 B 장면 통합..."] },
      "model": "gpt-4o",
      "cost": 0.005,
      "tokens": 3500
    }
    ``` 