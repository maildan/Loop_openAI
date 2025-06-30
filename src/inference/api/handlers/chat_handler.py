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
from typing import TypedDict, Literal, Any
from openai import AsyncOpenAI
from .web_search_handler import WebSearchHandler, SearchResult as WebSearchResult

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

    def load_datasets(self):
        """네이버 데이터셋 로딩"""
        try:
            # naver.jsonl 로딩
            naver_path = "dataset/naver/naver.jsonl"
            if os.path.exists(naver_path):
                with open(naver_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            data: NaverWebtoonData = json.loads(line.strip())
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
                            data: NaverWebtoonData = json.loads(line.strip())
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

    async def handle_request(
        self, user_message: str, _history: list[ChatHistoryItem] | None = None
    ) -> dict[str, Any]:
        """사용자 요청을 처리하고 적절한 응답 생성"""
        intent, level = self.detect_intent_and_level(user_message)

        if intent == "greeting":
            return await self.handle_greeting()

        if intent == "web_search":
            search_summary, search_results = await self.web_search_handler.search(
                user_message
            )
            content = f"웹 검색 결과 요약:\n{search_summary}\n\n"
            for i, res in enumerate(search_results, 1):
                content += f"{i}. [{res.get('title', 'N/A')}]({res.get('url', '#')})\n"
                content += f"   - {res.get('snippet', '내용 없음')}\n"

            return {
                "response": content,
                "model": "rule-based",
                "cost": 0.0,
                "tokens": 0,
                "isComplete": True,
                "continuationToken": None,
                "metadata": {"intent": "web_search_result", "level": "N/A", "results_count": len(search_results)},
            }

        response_dict: dict[str, Any] | None = None
        if intent == "creation":
            response_dict = await self.generate_story_by_level(user_message, level)
        elif intent in ["technique", "feedback", "synopsis", "character"]:
            # 2/3단계: 기법/피드백/프로젝트
            prompt = self.create_practice_prompt(user_message, level)
            if level == "beginner":
                max_tokens = 500
                temperature = 0.7
            elif level == "intermediate":
                max_tokens = 1000
                temperature = 0.8
            else:  # advanced
                max_tokens = 1500
                temperature = 0.9
            response_dict = await self.generate_response(
                prompt, intent, level, max_tokens, temperature
            )
        else:  # general
            # 일반 대화 또는 의도 불분명
            response_dict = await self.handle_greeting()

        if response_dict:
            return response_dict

        # 기본적으로 스토리 생성으로 연결
        return await self.generate_story_by_level(user_message, level)

    async def handle_greeting(self) -> dict[str, Any]:
        """간단한 인사말 처리"""
        greetings = ["안녕하세요! 무엇을 도와드릴까요?", "반갑습니다! 어떤 이야기를 만들어 볼까요?"]
        return {
            "response": random.choice(greetings),
            "model": "rule-based",
            "cost": 0.0,
            "tokens": 0,
            "isComplete": True,
            "continuationToken": None,
            "metadata": {"intent": "greeting", "level": "beginner"},
        }

    async def generate_story_by_level(
        self,
        user_message: str,
        level: str,
        max_tokens: int = 4000,
        is_long_form: bool = False,
        continue_story: bool = False,
    ) -> dict[str, Any]:
        """
        사용자 레벨에 맞춰 스토리 생성 프롬프트를 만들고 실행
        """
        style, length = self.extract_style_and_length(user_message)
        prompt = ""
        if level == "beginner":
            prompt = self.create_beginner_story_prompt(
                user_message, style, length, is_long_form, continue_story
            )
        elif level == "intermediate":
            prompt = self.create_intermediate_story_prompt(
                user_message, style, length, is_long_form, continue_story
            )
        else:  # advanced
            prompt = self.create_advanced_story_prompt(
                user_message, style, length, is_long_form, continue_story
            )

        return await self.generate_response(
            prompt, "creation", level, max_tokens, 0.75
        )

    def create_beginner_story_prompt(
        self,
        user_message: str,
        style: str,
        length: str,
        is_long_form: bool = False,
        continue_story: bool = False,
    ) -> str:
        """초보자용 스토리 프롬프트 - 간단하고 명확하게"""

        mode_instruction = ""
        if is_long_form:
            mode_instruction = """
**📖 긴 소설 모드 활성화**
- 더 길고 상세한 이야기 생성
- 여러 문단으로 구성된 플롯
"""

        if continue_story:
            mode_instruction += """
**🔄 이야기 계속하기 모드**
- 이전 맥락을 자연스럽게 이어가기
- 기존 캐릭터와 설정 유지
- 스토리 일관성 보장
- 새로운 전개 요소 추가
"""

        return f"""당신은 초보 작가를 격려하는 친근한 선생님입니다.

**요청:** {user_message}
**스타일:** {style}
**길이:** {length}
{mode_instruction}

**✅ 당신이 해야 할 일:**

**1️⃣ 단계: 이야기 생성**
먼저, 위의 요청에 따라 이야기를 완성해주세요. 시작-중간-끝 구조를 갖춘 명확한 이야기를 만들어주세요.

**2️⃣ 단계: 분석 및 피드백**
이야기 생성이 **완전히 끝난 후**, 아래 형식에 맞춰 분석과 피드백을 제공해주세요.
---
**[이야기 분석]**

**1. 이 이야기의 좋은 점 (3가지):**
   - 
   - 
   - 

**2. 다음 글쓰기 연습 제안:**
   - 

**3. 따뜻한 격려 메시지:**
   - 
---

자, 이제 1단계부터 시작하여 이야기를 작성해주세요. 당신의 멋진 이야기를 기다리고 있겠습니다!"""

    def create_intermediate_story_prompt(
        self,
        user_message: str,
        style: str,
        length: str,
        is_long_form: bool = False,
        continue_story: bool = False,
    ) -> str:
        """중급자용 스토리 프롬프트 - 기법 연습 중심"""

        focus_technique = "대화, 묘사, 페이싱 중 1개 선택"  # 이 부분은 실제 로직에서 동적으로 결정될 수 있음

        mode_instruction = ""
        if is_long_form:
            mode_instruction = """
**📖 긴 소설 모드 활성화**
- 특정 기법을 중심으로 한 심층적인 이야기
- 복잡한 플롯과 캐릭터 관계
"""

        if continue_story:
            mode_instruction += """
**🔄 이야기 계속하기 모드**
- 선택된 기법을 중심으로 이야기 확장
- 심화된 플롯과 캐릭터 개발
- 복선 및 반전 요소 고려
"""

        return f"""당신은 숙련된 글쓰기 멘토입니다. 중급 작가의 기법 향상을 돕습니다.

**요청:** {user_message}
**스타일:** {style}
**길이:** {length}
**이번 연습의 핵심 기법:** {focus_technique}

**✅ 당신이 해야 할 일:**

**1️⃣ 단계: 이야기 생성**
먼저, 위의 요청에 따라 이야기를 완성해주세요. 특히 **{focus_technique}** 기법을 의식적으로 활용하여 작성해주세요.

**2️⃣ 단계: 분석 및 피드백**
이야기 생성이 **완전히 끝난 후**, 아래 형식에 맞춰 분석과 피드백을 제공해주세요.
---
**[기법 분석]**

**1. {focus_technique} 기법이 어떻게 사용되었나요?**
   - 

**2. 이 기법을 더 발전시키기 위한 제안:**
   - 

**3. 다음 도전 과제:**
   - 
---

자, 이제 1단계부터 시작하여 이야기를 작성해주세요. 당신의 실력을 보여주세요!"""

    def create_advanced_story_prompt(
        self,
        user_message: str,
        style: str,
        length: str,
        is_long_form: bool = False,
        continue_story: bool = False,
    ) -> str:
        """고급자용 스토리 프롬프트 - 완성도와 독창성 중심"""
        mode_instruction = ""

        if is_long_form:
            mode_instruction = """
**📖 긴 소설 모드 활성화**
- 출판 가능한 수준의 완성도 높은 장편
- 독창적인 세계관과 깊이 있는 캐릭터
"""

        if continue_story:
            mode_instruction += """
**🔄 이야기 계속하기 모드**
- 작품의 완성도를 높이는 방향으로 전개
- 독자 반응과 시장성 고려
- 플롯의 개연성과 일관성 강화
"""

        return f"""당신은 전문 편집자 또는 작가 에이전트입니다. 고급 작가의 작품 완성도를 높입니다.

**요청:** {user_message}
**스타일:** {style}
**길이:** {length}
**핵심 목표:** 독창성, 완성도, 그리고 시장성

**✅ 당신이 해야 할 일:**

**1️⃣ 단계: 이야기 생성**
먼저, 위의 요청에 따라 이야기를 완성해주세요. 이 작품이 출간된다고 가정하고, 프로 수준의 독창성과 완성도를 보여주세요.

**2️⃣ 단계: 작품성 분석 및 제언**
이야기 생성이 **완전히 끝난 후**, 아래 형식에 맞춰 날카로운 분석과 현실적인 제언을 제공해주세요.
---
**[작품 분석]**

**1. 이 작품의 시장 경쟁력과 독창성:**
   - 

**2. 상업적 성공을 위해 보완할 점:**
   - 

**3. 다음 단계 제언 (출판사 투고, 플랫폼 연재 등):**
   - 
---

자, 이제 1단계부터 시작하여 당신의 역량을 보여줄 작품을 만들어주세요."""

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

    async def generate_response(
        self, prompt: str, intent: str, level: str, max_tokens: int, temperature: float
    ) -> dict[str, Any]:
        """
        OpenAI API를 사용하여 응답을 생성하고, 비용과 토큰 사용량을 계산하여
        server.py의 ChatResponse 모델과 호환되는 딕셔너리를 반환합니다.
        """
        if not self.client:
            logger.warning("⚠️ OpenAI 클라이언트가 설정되지 않아 기본 응답을 반환합니다.")
            return {
                "response": "OpenAI 클라이언트가 설정되지 않았습니다. 관리자에게 문의하세요.",
                "model": "N/A",
                "cost": 0.0,
                "tokens": 0,
                "isComplete": True,
                "continuationToken": None,
            }

        try:
            completion = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            content = completion.choices[0].message.content or ""
            model = completion.model or "gpt-4o-mini"
            prompt_tokens = completion.usage.prompt_tokens if completion.usage else 0
            completion_tokens = (
                completion.usage.completion_tokens if completion.usage else 0
            )
            total_tokens = completion.usage.total_tokens if completion.usage else 0

            # 비용 계산 (server.py의 로직과 유사하게)
            # 이 부분은 단순화를 위해 실제 server.py의 calculate_cost 함수를 호출하거나
            # 동일한 로직을 여기에 구현해야 합니다. 여기서는 간소화된 예시를 사용합니다.
            cost = (prompt_tokens * 0.00015 + completion_tokens * 0.0006) / 1000

            # server.py의 ChatResponse 모델과 호환되는 딕셔너리 반환
            return {
                "response": content.strip(),
                "model": model,
                "cost": cost,
                "tokens": total_tokens,
                "isComplete": True, # 기본적으로 완료로 설정
                "continuationToken": None, # 현재는 지원하지 않음
                # --- 기존 metadata 정보도 포함 가능 ---
                "metadata": {
                    "intent": intent,
                    "level": level,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                }
            }

        except Exception as e:
            logger.error(f"❌ OpenAI API 호출 오류: {e}")
            return {
                "response": "죄송합니다, AI 모델과 통신하는 중 오류가 발생했습니다.",
                "model": "error",
                "cost": 0.0,
                "tokens": 0,
                "isComplete": True,
                "continuationToken": None,
            }

    def test_intent_detection(self) -> dict[str, tuple[str, str]]:
        """의도 감지 기능 테스트"""
        test_cases = {
            "안녕하세요": ("greeting", "beginner"),
            "새로운 소설 아이디어 좀 주세요": ("creation", "beginner"),
            "내 캐릭터가 너무 평면적인데 어떻게 입체적으로 만들죠?": ("technique", "intermediate"),
            "지금 쓰는 시놉시스 피드백 부탁해요": ("feedback", "advanced"),
            "최신 AI 기술 뉴스 찾아줘": ("web_search", "beginner"),
        }
        results = {}
        for text, expected in test_cases.items():
            results[text] = self.detect_intent_and_level(text)
            assert results[text] == expected
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
