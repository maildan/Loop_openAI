# 🦾 GigaChad급 OpenAI 비용 최적화 가이드

> "돈을 태우기 전에 뇌부터 굴려라." – GigaChad

---

## 1. 핵심 요약

* GPT-4o-mini 기준 **입력 1M 토큰 $0.15 / 출력 1M 토큰 $0.60** (2025-01 가격).
* 평균 프롬프트 200토큰 + 응답 800토큰이면 **1회 $0.0005 → 하루 100회 ≈ $0.05, 월 3,000회 ≈ $1.50**.
* 잘 설계된 캐싱·배치·로컬 하이브리드로 **70-90 %** 절감 가능.

---

## 2. 실전 단가 계산 예시
```python
# requirements: tiktoken==0.6.0, openai>=1.0.0
import openai, tiktoken

COST = {
    "input": 0.15 / 1_000_000,
    "output": 0.60 / 1_000_000,
}

usage = {"input_tokens": 200, "output_tokens": 800}

cost = usage["input_tokens"] * COST["input"] + usage["output_tokens"] * COST["output"]
print(f"한 번 호출 비용: ${cost:.4f}")  # → $0.0005
```

---

## 3. GigaChad 전략별 절감 비율

| 전략 | 예상 절감 | 요점 |
|------|-----------|------|
| ✂️ 토큰 다이어트 | 30-50 % | 쓸모없는 수식어·장황 프롬프트 제거 |
| 🔀 모델 스위칭 | 20-60 % | GPT-4o ↔ GPT-4o-mini ↔ GPT-3.5-turbo 적절히 사용 |
| 💾 캐싱 | ~50 % | 동일한 1,024+ 토큰 프롬프트 재사용 시 자동 50 % 할인 |
| 📦 배치(Batch API) | 50 % | 한 번에 여러 요청 처리, 24 h SLA |
| 🏠 로컬 모델 라우팅 | 70 %+ | 간단 요청은 Ollama·GGUF 등 무료 처리 |
| 🆓 Freemium 요금제 | 비용 전가 | 무료 구간+유료 티어로 API 비용 상쇄 |

---

## 4. 핵심 코드 스니펫 모음

### 4-1. 프롬프트 토큰 최적화 함수
```python
def optimize_prompt(user_msg: str) -> str:
    """장황 문구 제거로 토큰 80 % 절감"""
    return f"한국어 창작 전문가로서 아래 요청에 응답하세요:\n{user_msg}"
```

### 4-2. 캐싱 + LRU
```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def cached_chat(prompt: str, model: str = "gpt-4o-mini") -> str:
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```

### 4-3. 배치 처리
```python
def batch_chat(prompts: list[str]) -> list[str]:
    job = openai.beta.batch.create(
        input=[{"custom_id": str(i), "method": "POST", "url": "/v1/chat/completions", "body": {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": p}]
        }} for i, p in enumerate(prompts)],
    )
    return [task.response.choices[0].message.content for task in job.output()]
```

### 4-4. 하이브리드 라우팅
```python
def smart_generate(prompt: str) -> str:
    """복잡도 낮으면 로컬 모델, 높으면 OpenAI"""
    simple = len(prompt) < 120 and prompt.endswith("?")
    if simple:
        return local_llm.generate(prompt)  # 비용 $0
    else:
        return cached_chat(prompt)         # 캐시·배치 적용
```

---

## 5. 통합 비용-제어 클래스 예시
```python
class CostAwareAI:
    MONTHLY_LIMIT = 50  # USD

    def __init__(self):
        self.spend = 0
        self.cache = {}

    def generate(self, prompt: str, user_id: str):
        key = prompt.strip().lower()
        if key in self.cache:
            return self.cache[key]

        if self.spend > self.MONTHLY_LIMIT:
            return local_llm.generate(prompt)

        result = cached_chat(prompt)
        self.cache[key] = result
        self.spend += estimate_cost(prompt, result)
        return result
```

---

## 6. 추가 리소스

* OpenAI 공식 배치 가이드 – 50 % 할인 <https://platform.openai.com/docs/guides/batch>
* 커뮤니티 토론: API 비용 관리 노하우 <https://community.openai.com/t/looking-for-feedback-managing-openai-api-costs-and-usage/380119>  
* 비용 최적화 실전 블로그 <https://medium.com/@mikehpg/controlling-cost-when-using-openai-api-fd5a038fa391>  
* FinOps 관점 비용 분석 <https://www.cloudzero.com/blog/openai-cost-optimization/>

---

## 7. TODO (DevOps)

1. `docs/` → mkdocs 배포 파이프라인에 포함.
2. 월간 `openai_usage.csv` 생성 후 Grafana 대시보드 연동.
3. `CostAwareAI` 클래스를 `src/utils/openai_wrapper.py` 에 통합.

---

### 끝. 이제 돈 태우지 말고 **지혜롭게 태워라🔥** 