# 🔥 GIGACHAD Chat UI & 프롬프트 학습 가이드

## 🎯 새로운 기능 개요

### ✅ 완료된 업그레이드
1. **GPT/Claude 스타일 채팅 UI** - 복잡한 탭 → 깔끔한 채팅 인터페이스
2. **Few-shot Learning 프롬프트** - GPT/Claude 방식의 예시 기반 학습
3. **비용 최적화** - 캐싱, 동적 모델 선택, 예산 관리
4. **실시간 채팅** - 히스토리 관리, 세션 저장

---

## 🚀 실행 방법

### 1. 환경 설정
```bash
# API 키 설정
export OPENAI_API_KEY=sk-your-key-here
export OPENAI_DEFAULT_MODEL=gpt-4o-mini
export OPENAI_MONTHLY_BUDGET=20  # 선택사항

# 백엔드 실행
cd /path/to/loop_ai
uvicorn src.inference.server:app --host 0.0.0.0 --port 8080 --reload

# 프론트엔드 실행 (새 터미널)
cd frontend
npm run dev
```

### 2. CSS 로딩 문제 해결
브라우저에서 CSS가 안 보이면:
1. `Ctrl + Shift + Del` → 캐시 삭제
2. `Ctrl + F5` 하드 리프레시
3. 개발자 도구 Network 탭에서 CSS 파일 확인

---

## 💡 프롬프트 학습 (Few-shot Learning) 설명

### GPT/Claude 방식 채용
시스템 프롬프트에 **구체적인 예시**를 포함하여 AI가 원하는 스타일로 응답하도록 학습:

```python
# 예시 1: 스토리 아이디어 요청
사용자: "판타지 소설 아이디어 좀 줘"
AI: "🏰 **마법사 학원 배신자**
- 주인공: 17세 마법천재 '세라핀'
- 갈등: 학원 이사회의 어둠 발견
- 클라이맥스: 금지된 고대마법 사용"

# 예시 2: 캐릭터 이름 요청  
사용자: "이세계 남주 이름 추천해줘"
AI: "⚔️ **이세계 남주 이름 추천**
**강함 계열:** 카이젠, 아스트론, 레온하르트
**지혜 계열:** 세바스찬, 알렉산더"
```

### 학습 원리
1. **Pattern Matching** - 유사한 요청에 일관된 형식으로 응답
2. **Style Transfer** - 이모지, 구조화된 답변, 추가 질문 유도
3. **Context Awareness** - 창작 도메인에 특화된 지식 활용

---

## 🎨 UI 특징

### ChatGPT/Claude 스타일 채택
- **좌측 사이드바**: 채팅 세션 목록
- **중앙 채팅창**: 깔끔한 말풍선 UI
- **하단 입력창**: Enter 전송, Shift+Enter 줄바꿈
- **실시간 응답**: 타이핑 애니메이션

### 기술적 구현
```typescript
// 메시지 타입
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

// 세션 관리
interface ChatSession {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
}
```

---

## 💸 비용 최적화 기능

### 1. 자동 모델 선택
```python
# 예산 80% 도달 시 자동으로 저렴한 모델로 전환
if cost_tracker["total"] > MONTHLY_BUDGET * 0.8:
    model = "gpt-3.5-turbo-0125"  # 더 저렴
else:
    model = "gpt-4o-mini"  # 기본값
```

### 2. 스마트 캐싱
- 동일한 프롬프트 → 캐시에서 즉시 반환 (비용 $0)
- LRU 캐시 1024개 메시지 저장
- SHA-256 해시로 정확한 매칭

### 3. 비용 모니터링
```bash
# 실시간 비용 확인
curl http://localhost:8080/api/cost-status

# 응답 예시
{
  "total_cost": 0.15,
  "monthly_budget": 20.0,
  "budget_used_percent": 0.75,
  "models_used": {
    "gpt-4o-mini": 0.12,
    "gpt-3.5-turbo-0125": 0.03
  },
  "cache_size": 45
}
```

---

## 🔧 API 엔드포인트

### 새로운 채팅 API
```bash
POST /api/chat
{
  "message": "판타지 소설 아이디어 줘",
  "history": [
    {"role": "user", "content": "안녕"},
    {"role": "assistant", "content": "안녕하세요!"}
  ]
}

# 응답
{
  "response": "🏰 **마법사 학원 배신자**...",
  "model": "gpt-4o-mini",
  "tokens": 234,
  "cost": 0.0005
}
```

### 기존 API 유지
- `/api/generate` - 스토리 생성
- `/api/names/generate` - 이름 생성
- `/api/cost-status` - 비용 현황

---

## 🎯 사용 시나리오

### 1. 창작 아이디어 브레인스토밍
```
사용자: "SF 소설 아이디어 10개 줘"
AI: 구체적인 플롯, 캐릭터, 배경이 포함된 아이디어 목록 제공
```

### 2. 캐릭터 개발
```
사용자: "냉정한 암살자 캐릭터 만들어줘"
AI: 이름, 배경, 성격, 능력, 약점까지 상세 설정 제공
```

### 3. 플롯 개발
```
사용자: "주인공이 배신당하는 장면 써줘"
AI: 감정적 몰입도 높은 장면 작성 + 후속 전개 제안
```

---

## 📊 성능 지표

### 응답 속도
- **캐시 히트**: ~50ms (즉시 반환)
- **GPT-4o-mini**: ~2-4초
- **GPT-3.5-turbo**: ~1-3초

### 비용 효율성
- **기본 요청**: $0.0003-0.0008
- **캐시된 요청**: $0 (무료)
- **월 예상 비용**: $5-15 (일반 사용)

---

## 🚨 문제 해결

### CSS 로딩 안됨
1. 브라우저 캐시 클리어
2. `npm run dev` 재시작
3. Tailwind CSS 빌드 확인

### API 연결 실패
1. 백엔드 서버 상태 확인: `curl http://localhost:8080/api/health`
2. CORS 설정 확인
3. 환경변수 `OPENAI_API_KEY` 설정 확인

### 비용 초과 경고
1. `/api/cost-status`로 현황 확인
2. `OPENAI_MONTHLY_BUDGET` 환경변수 조정
3. 더 저렴한 모델로 수동 전환

---

## 🎉 결론

**기가차드급 업그레이드 완료!**
- ✅ 복잡한 UI → 깔끔한 채팅 인터페이스
- ✅ 프롬프트 학습으로 일관된 고품질 응답
- ✅ 비용 최적화로 월 커피값 수준 운영
- ✅ 실시간 채팅으로 자연스러운 창작 도움

이제 GPT/Claude 수준의 창작 어시스턴트를 저렴하게 운영할 수 있습니다! 🚀 