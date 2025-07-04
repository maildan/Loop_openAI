"""
Loop AI 채팅 처리 핸들러 - Jane Friedman 3단계 프롬프트 방법론 적용
1. Build Stamina Through Practice (실습을 통한 체력 구축)
2. Develop Mastery of Techniques (기법 숙련도 개발)
3. Apply Prompts to Projects (프로젝트에 적용)
"""

import json
import logging
import os
import random
import re
import time
from typing import TypedDict, cast, Any
from collections.abc import AsyncGenerator
from openai import AsyncOpenAI, APIConnectionError
from openai.types.chat import ChatCompletionMessageParam
from .web_search_handler import WebSearchHandler, SearchResult as WebSearchResult
from src.shared.prompts.loader import get_prompt, get_system_prompt

logger = logging.getLogger(__name__)

# --- TypedDicts for Data Structures ---
class NaverWebtoonData(TypedDict):
    """네이버 웹툰 데이터셋의 단일 항목 구조"""
    title: str
    summary: str
    text: str # 'text'는 'summary'와 동일한 내용을 가질 수 있음
    genre: str
    url: str

class ChatHistoryItem(TypedDict):
    role: str
    content: str


class ChatHandler:
    """전문 작가용 채팅 처리 핸들러 - 실용적 창작 도구"""

    client: AsyncOpenAI | None
    web_search_handler: WebSearchHandler
    naver_dataset: list[NaverWebtoonData]
    naver_challenge_dataset: list[NaverWebtoonData]
    practice_prompts: dict[str, str]
    system_prompt: str

    def __init__(self, openai_client: AsyncOpenAI | None = None):
        """
        채팅 핸들러 초기화

        Args:
            openai_client: AsyncOpenAI 클라이언트 인스턴스
        """
        self.client = openai_client
        self.web_search_handler = WebSearchHandler(openai_client)
        self.naver_dataset = []
        self.naver_challenge_dataset = []

        # Jane Friedman 방법론 기반 프롬프트 카테고리
        self.practice_prompts = {
            "basic_exercise": "기본 연습 - 글쓰기 근육 만들기",
            "technique_focus": "기법 집중 - 특정 기술 연마",
            "project_application": "프로젝트 적용 - 실제 작업에 활용",
        }

        # 시스템 프롬프트 로드
        self.system_prompt = get_system_prompt()
        logger.info("✅ Master System Prompt 로드 완료")

    def load_datasets(self):
        """네이버 데이터셋 로딩"""
        try:
            # naver.jsonl 로딩
            naver_path = "dataset/naver/naver.jsonl"
            if os.path.exists(naver_path):
                with open(naver_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            # json.loads가 Any를 반환하므로 명시적으로 캐스팅
                            data = cast(NaverWebtoonData, json.loads(line.strip()))
                            self.naver_dataset.append(data)
                        except (json.JSONDecodeError, TypeError):
                            continue
                logger.info(
                    f"📚 네이버 웹툰 데이터셋 로딩 완료: {len(self.naver_dataset)}개 항목"
                )

            # naver_challenge.jsonl 로딩
            challenge_path = "dataset/naver/naver_challenge.jsonl"
            if os.path.exists(challenge_path):
                with open(challenge_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            data = cast(NaverWebtoonData, json.loads(line.strip()))
                            self.naver_challenge_dataset.append(data)
                        except (json.JSONDecodeError, TypeError):
                            continue
                logger.info(
                    f"🏆 네이버 도전만화 데이터셋 로딩 완료: {len(self.naver_challenge_dataset)}개 항목"
                )

        except Exception as e:
            logger.error(f"❌ 데이터셋 로딩 오류: {e}")

    def get_relevant_examples(self, _query: str, num_examples: int = 3) -> list[str]:
        """쿼리와 관련된 예시를 데이터셋에서 추출"""
        if not self.naver_dataset and not self.naver_challenge_dataset:
            return []

        # 간단한 키워드 매칭으로 관련 예시 추출
        _keywords = ["시놉시스", "줄거리", "요약", "스토리", "내용"]
        relevant_examples: list[str] = []

        dataset = self.naver_dataset + self.naver_challenge_dataset

        for item in dataset:
            text = item.get("text", "")
            if any(keyword in text for keyword in _keywords):
                relevant_examples.append(text)
                if len(relevant_examples) >= num_examples:
                    break

        # 충분한 예시가 없으면 랜덤 선택
        if len(relevant_examples) < num_examples and dataset:
            remaining = min(num_examples - len(relevant_examples), len(dataset))
            random_samples: list[NaverWebtoonData] = random.sample(dataset, remaining)
            for sample in random_samples:
                relevant_examples.append(sample.get("text", ""))

        return relevant_examples[:num_examples]

    def detect_intent_and_level(self, user_message: str) -> tuple[str, str]:
        """사용자 의도와 작가 레벨 감지"""

        # 입력 길이 및 의미 있는 내용 체크
        cleaned_message = user_message.strip()

        # 무의미한 입력 감지 (더 엄격하게)
        meaningless_patterns = [
            r"^[ㅎㅇㅋㅜㅠㅏㅓㅗㅜㅣ]{1,10}$",
            r"^[ㅋㅎㅇ]{1,10}$",
            r'^[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]{1,10}$',
            r"^[0-9]{1,3}$",
            r"^[a-zA-Z]{1,3}$",
        ]

        for pattern in meaningless_patterns:
            if re.match(pattern, cleaned_message):
                return "greeting", "beginner"

        if len(cleaned_message) < 5:  # 더 엄격한 최소 길이
            return "greeting", "beginner"

        # 작가 레벨 감지 (Jane Friedman 3단계 기반)
        level_indicators = {
            "beginner": ["처음", "시작", "배우고 싶", "어떻게", "기초", "초보"],
            "intermediate": ["연습", "기법", "테크닉", "스타일", "개선", "향상"],
            "advanced": ["프로젝트", "작품", "출간", "완성", "전문적", "심화"],
        }

        detected_level = "beginner"  # 기본값
        for level, keywords in level_indicators.items():
            if any(keyword in cleaned_message for keyword in keywords):
                detected_level = level
                break

        # 명확한 창작 의도 키워드 (더 포괄적으로)
        creation_keywords = [
            "이야기",
            "소설",
            "스토리",
            "창작",
            "써줘",
            "만들어",
            "시나리오",
            "웹툰",
            "소설 써",
            "이야기 만들",
        ]

        if any(keyword in cleaned_message for keyword in creation_keywords):
            return "creation", detected_level

        # 기타 의도 분류
        intent_keywords = {
            "synopsis": ["시놉시스", "줄거리", "요약", "내용 정리"],
            "character": ["캐릭터", "인물", "등장인물", "주인공"],
            "technique": ["기법", "테크닉", "방법", "어떻게 써"],
            "feedback": ["피드백", "평가", "검토", "의견"],
            "web_search": ["검색", "찾아줘", "알려줘", "최신", "뉴스"],
        }

        for intent, keywords in intent_keywords.items():
            if any(keyword in cleaned_message for keyword in keywords):
                return intent, detected_level

        return "general", detected_level

    def create_practice_prompt(self, user_message: str, level: str) -> str:
        """1단계: 실습을 통한 체력 구축 프롬프트"""

        if level == "beginner":
            return f"""당신은 친근한 글쓰기 코치입니다. 초보 작가를 위한 기본 연습을 도와주세요.

사용자 요청: {user_message}

**초보자용 접근법:**
1. 간단하고 명확한 지침 제공
2. 부담스럽지 않은 분량 (300-500자)
3. 구체적인 예시 포함
4. 격려와 동기부여 메시지

**연습 목표:** 
- 매일 조금씩 쓰는 습관 만들기
- 완벽하지 않아도 완성하는 경험
- 글쓰기에 대한 두려움 줄이기

친근하고 격려하는 톤으로 도움을 주세요."""

        elif level == "intermediate":
            return f"""당신은 경험 있는 글쓰기 멘토입니다. 중급 작가의 기법 향상을 도와주세요.

사용자 요청: {user_message}

**중급자용 접근법:**
1. 특정 기법에 집중한 연습
2. 적당한 도전 과제 (500-800자)
3. 다양한 관점과 스타일 실험
4. 구체적인 개선점 제시

**연습 목표:**
- 특정 기법 마스터하기 (대화, 묘사, 관점 등)
- 같은 주제로 다른 방식 시도
- 자신만의 스타일 찾기

전문적이면서도 실용적인 조언을 제공하세요."""

        else:  # advanced
            return f"""당신은 전문 작가 동료입니다. 고급 작가의 프로젝트 완성을 도와주세요.

사용자 요청: {user_message}

**고급자용 접근법:**
1. 실제 프로젝트에 적용 가능한 조언
2. 심화된 기법과 전략 (800-1200자)
3. 출간/발표를 위한 완성도 추구
4. 독창성과 완성도 균형

**연습 목표:**
- 현재 작업 중인 프로젝트 개선
- 출간 가능한 수준의 완성도
- 독자 반응을 고려한 전략적 접근

동료 작가로서 전문적이고 깊이 있는 피드백을 주세요."""

    def create_technique_focused_prompt(
        self, user_message: str, _technique: str
    ) -> str:
        """2단계: 기법 숙련도 개발 프롬프트"""

        technique_guides = {
            "dialogue": {
                "focus": "대화 기법",
                "exercise": "같은 상황을 다른 캐릭터 관점에서 대화로만 표현",
                "tips": "각 캐릭터의 독특한 말투, 숨겨진 감정, 갈등 표현",
            },
            "description": {
                "focus": "묘사 기법",
                "exercise": "오감을 모두 활용한 장면 묘사",
                "tips": "구체적 디테일, 감정과 연결된 묘사, 독자 몰입",
            },
            "pov": {
                "focus": "시점 기법",
                "exercise": "같은 사건을 1인칭, 3인칭, 전지적 관점으로 각각 써보기",
                "tips": "각 시점의 장단점, 독자와의 거리감, 정보 전달 방식",
            },
            "pacing": {
                "focus": "속도 조절",
                "exercise": "긴장감 있는 장면과 여유로운 장면 대비",
                "tips": "문장 길이 조절, 리듬감, 독자의 호흡 고려",
            },
        }

        # 사용자 메시지에서 기법 유형 추출
        detected_technique = "dialogue"  # 기본값
        for tech, data in technique_guides.items():
            if tech in user_message.lower() or data["focus"] in user_message:
                detected_technique = tech
                break

        guide = technique_guides[detected_technique]

        return f"""당신은 {guide['focus']} 전문 강사입니다.

사용자 요청: {user_message}

**{guide['focus']} 마스터 과정:**

📝 **연습 방법:** {guide['exercise']}

💡 **핵심 포인트:**
{guide['tips']}

**실습 단계:**
1. 먼저 기본 버전을 써보세요
2. 다른 접근법으로 같은 내용을 다시 써보세요  
3. 두 버전을 비교하며 차이점을 분석하세요
4. 가장 효과적인 부분을 찾아보세요

**평가 기준:**
- 기법의 정확한 적용
- 독자에게 미치는 효과
- 전체 스토리와의 조화

단계별로 차근차근 안내해주세요."""

    def create_project_application_prompt(self, user_message: str) -> str:
        """3단계: 프로젝트에 적용 프롬프트"""
        return f"""당신은 유능한 편집자이자 출판 컨설턴트입니다. 작가의 실제 프로젝트를 출간 가능한 수준으로 끌어올리는 것을 도와주세요.

사용자 프로젝트 설명: {user_message}

**프로젝트 적용 단계의 핵심 목표:**
- **시장성 분석:** 독자들이 원하는 것과 작가의 아이디어를 연결합니다.
- **구조적 완성도:** 플롯, 캐릭터 아크, 페이싱을 점검하고 강화합니다.
- **차별성 확보:** 기존 작품들과 차별화되는 독창적인 포인트를 부각시킵니다.
- **상업적 가치 증대:** 독자의 구매를 유도할 수 있는 매력적인 요소를 제안합니다.

전문적인 편집자의 관점에서 날카롭고 건설적인 피드백과 아이디어를 제공해주세요."""

    async def handle_web_search(self, user_message: str) -> AsyncGenerator[str, None]:
        """웹 검색을 처리하고 결과를 단일 청크로 yield하는 비동기 제너레이터"""
        search_summary, search_results = await self.web_search_handler.search(
            user_message
        )
        content = f"**웹 검색 결과 요약:**\n{search_summary}\n\n"
        for i, res in enumerate(search_results, 1):
            title = res.get('title', 'N/A')
            url = res.get('url', '#')
            snippet = res.get('snippet', '내용 없음')
            content += f"{i}. **[{title}]({url})**\n   - {snippet}\n"
        yield content

    async def generate_response(
        self, prompt: str, max_tokens: int, temperature: float
    ) -> AsyncGenerator[str, None]:
        """
        주어진 프롬프트를 사용하여 OpenAI API로부터 스트리밍 응답을 생성합니다.

        Args:
            prompt (str): AI에 전달할 최종 프롬프트 문자열.
            max_tokens (int): 생성할 최대 토큰 수.
            temperature (float): 샘플링 온도.
        """
        if not self.client:
            yield "OpenAI client is not initialized."
            return

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        try:
            logger.info(f"🚀 OpenAI API 요청 시작: max_tokens={max_tokens}, temperature={temperature}")
            stream = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
            logger.info("✅ OpenAI API 스트리밍 응답 완료")
        except APIConnectionError as e:
            logger.error(f"❌ OpenAI API 연결 오류: {e.__cause__}")
            yield f"Error: Could not connect to OpenAI API. {e.__cause__}"
        except Exception as e:
            logger.error(f"❌ 응답 생성 중 예상치 못한 오류 발생: {e}", exc_info=True)
            yield f"Error: An unexpected error occurred. {e}"

    def extract_style_and_length(self, user_message: str) -> tuple[str, str]:
        """사용자 메시지에서 스타일과 길이 추출"""

        # 스타일 키워드
        styles = {
            "판타지": ["판타지", "마법", "드래곤"],
            "SF": ["SF", "우주", "미래", "로봇"],
            "로맨스": ["로맨스", "사랑", "연애"],
            "스릴러": ["스릴러", "긴장감", "추리"],
            "코믹": ["코믹", "웃긴", "개그"],
        }

        detected_style = "지정되지 않음"
        for style, keywords in styles.items():
            if any(keyword in user_message for keyword in keywords):
                detected_style = style
                break
        
        style_and_length = (detected_style, "알 수 없음")
        if "알 수 없음" in style_and_length:
             # 임시 로직: 실제로는 길이도 감지해야 함
            pass

        # 길이 키워드
        lengths = {
            "짧은": ["짧은", "간단한", "짧게", "요약"],
            "긴": ["긴", "자세한", "길게", "상세한"],
            "중간": ["중간", "적당한", "보통"],
        }

        detected_length = "알 수 없음"
        for length, keywords in lengths.items():
            if any(keyword in user_message for keyword in keywords):
                detected_length = length
                break

        return detected_style, detected_length

    def clear_cache(self):
        """인스턴스의 캐시를 비웁니다."""
        # 캐싱 로직이 스트리밍으로 인해 제거되었으므로, 이 함수는 현재 아무 작업도 하지 않습니다.
        # 나중에 스트리밍을 지원하는 새로운 캐싱 전략이 도입될 경우를 위해 남겨둡니다.
        logger.info("캐시 비우기 호출됨 (스트리밍 모드에서는 비활성 상태)")

    def test_intent_detection(self) -> dict[str, tuple[str, str]]:
        """의도 감지 기능 테스트"""
        test_cases: dict[str, tuple[str, str]] = {
            "안녕하세요": ("greeting", "beginner"),
            "소설 어떻게 시작하죠?": ("technique", "beginner"),
            "내 주인공 캐릭터 좀 만들어줘": ("character", "intermediate"),
            "시놉시스 초안 피드백 부탁해": ("feedback", "advanced"),
            "최신 SF 소설 트렌드 알려줘": ("web_search", "intermediate"),
            "ㅋㅋㅋ": ("greeting", "beginner"),
        }
        results: dict[str, tuple[str, str]] = {}
        for test_case, expected in test_cases.items():
            results[test_case] = self.detect_intent_and_level(test_case)
            assert results[test_case] == expected, f"테스트 실패: '{test_case}'"
        logger.info("✅ 의도 감지 테스트 통과")
        return results

    def get_prompt_stats(self, prompt: str) -> dict[str, int]:
        """프롬프트의 단어 수와 글자 수 계산"""
        word_count = len(prompt.split())
        char_count = len(prompt)
        return {"words": word_count, "chars": char_count}

    def detect_level(self, user_message: str) -> str:
        """사용자 메시지에서 작가 레벨 감지"""
        level_indicators = {
            "beginner": ["처음", "시작", "배우고 싶어요", "어떻게 하나요"],
            "intermediate": ["연습", "기법", "스타일", "개선"],
            "advanced": ["프로젝트", "작품", "출간", "완성"],
        }
        for level, keywords in level_indicators.items():
            if any(keyword in user_message for keyword in keywords):
                return level
        return "beginner"
