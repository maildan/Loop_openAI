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
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from .web_search_handler import WebSearchHandler # 웹 검색 핸들러 추가

logger = logging.getLogger(__name__)

class ChatHandler:
    """전문 작가용 채팅 처리 핸들러 - 실용적 창작 도구"""
    
    def __init__(self, openai_client: Optional[AsyncOpenAI] = None):
        """
        채팅 핸들러 초기화
        
        Args:
            openai_client: AsyncOpenAI 클라이언트 인스턴스
        """
        self.client = openai_client
        self.web_search_handler = WebSearchHandler(openai_client) # 웹 검색 핸들러 인스턴스 생성
        self.naver_dataset = []
        self.naver_challenge_dataset = []
        
        # Jane Friedman 방법론 기반 프롬프트 카테고리
        self.practice_prompts = {
            "basic_exercise": "기본 연습 - 글쓰기 근육 만들기",
            "technique_focus": "기법 집중 - 특정 기술 연마",
            "project_application": "프로젝트 적용 - 실제 작업에 활용"
        }
        
    def load_datasets(self):
        """네이버 데이터셋 로딩"""
        try:
            # naver.jsonl 로딩
            naver_path = "dataset/naver/naver.jsonl"
            if os.path.exists(naver_path):
                with open(naver_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            self.naver_dataset.append(data)
                        except json.JSONDecodeError:
                            continue
                logger.info(f"📚 네이버 웹툰 데이터셋 로딩 완료: {len(self.naver_dataset)}개 항목")
            
            # naver_challenge.jsonl 로딩
            challenge_path = "dataset/naver/naver_challenge.jsonl"
            if os.path.exists(challenge_path):
                with open(challenge_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            self.naver_challenge_dataset.append(data)
                        except json.JSONDecodeError:
                            continue
                logger.info(f"🏆 네이버 도전만화 데이터셋 로딩 완료: {len(self.naver_challenge_dataset)}개 항목")
                
        except Exception as e:
            logger.error(f"❌ 데이터셋 로딩 오류: {e}")
    
    def get_relevant_examples(self, query: str, num_examples: int = 3) -> List[str]:
        """쿼리와 관련된 예시를 데이터셋에서 추출"""
        if not self.naver_dataset and not self.naver_challenge_dataset:
            return []
        
        # 간단한 키워드 매칭으로 관련 예시 추출
        keywords = ["시놉시스", "줄거리", "요약", "스토리", "내용"]
        relevant_examples = []
        
        dataset = self.naver_dataset + self.naver_challenge_dataset
        
        for item in dataset:
            text = item.get("text", "")
            if any(keyword in text for keyword in keywords):
                relevant_examples.append(text)
                if len(relevant_examples) >= num_examples:
                    break
        
        # 충분한 예시가 없으면 랜덤 선택
        if len(relevant_examples) < num_examples and dataset:
            remaining = min(num_examples - len(relevant_examples), len(dataset))
            random_samples = random.sample(dataset, remaining)
            for sample in random_samples:
                relevant_examples.append(sample.get("text", ""))
        
        return relevant_examples[:num_examples]
    
    def detect_intent_and_level(self, user_message: str) -> tuple:
        """사용자 의도와 작가 레벨 감지"""
        
        # 입력 길이 및 의미 있는 내용 체크
        cleaned_message = user_message.strip()
        
        # 무의미한 입력 감지 (더 엄격하게)
        meaningless_patterns = [
            r'^[ㅎㅇㅋㅜㅠㅏㅓㅗㅜㅣ]{1,10}$',
            r'^[ㅋㅎㅇ]{1,10}$',
            r'^[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]{1,10}$',
            r'^[0-9]{1,3}$',
            r'^[a-zA-Z]{1,3}$',
        ]
        
        import re
        for pattern in meaningless_patterns:
            if re.match(pattern, cleaned_message):
                return "greeting", "beginner"
        
        if len(cleaned_message) < 5:  # 더 엄격한 최소 길이
            return "greeting", "beginner"
        
        # 작가 레벨 감지 (Jane Friedman 3단계 기반)
        level_indicators = {
            "beginner": ["처음", "시작", "배우고 싶", "어떻게", "기초", "초보"],
            "intermediate": ["연습", "기법", "테크닉", "스타일", "개선", "향상"],
            "advanced": ["프로젝트", "작품", "출간", "완성", "전문적", "심화"]
        }
        
        detected_level = "beginner"  # 기본값
        for level, keywords in level_indicators.items():
            if any(keyword in cleaned_message for keyword in keywords):
                detected_level = level
                break
        
        # 명확한 창작 의도 키워드 (더 포괄적으로)
        creation_keywords = [
            "이야기", "소설", "스토리", "창작", "써줘", "만들어",
            "시나리오", "웹툰", "소설 써", "이야기 만들"
        ]
        
        if any(keyword in cleaned_message for keyword in creation_keywords):
            return "creation", detected_level
        
        # 기타 의도 분류
        intent_keywords = {
            "synopsis": ["시놉시스", "줄거리", "요약", "내용 정리"],
            "character": ["캐릭터", "인물", "등장인물", "주인공"],
            "technique": ["기법", "테크닉", "방법", "어떻게 써"],
            "feedback": ["피드백", "평가", "검토", "의견"],
            "web_search": ["검색", "찾아줘", "알려줘", "최신", "뉴스"]
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

    def create_technique_focused_prompt(self, user_message: str, technique: str) -> str:
        """2단계: 기법 숙련도 개발 프롬프트"""
        
        technique_guides = {
            "dialogue": {
                "focus": "대화 기법",
                "exercise": "같은 상황을 다른 캐릭터 관점에서 대화로만 표현",
                "tips": "각 캐릭터의 독특한 말투, 숨겨진 감정, 갈등 표현"
            },
            "description": {
                "focus": "묘사 기법", 
                "exercise": "오감을 모두 활용한 장면 묘사",
                "tips": "구체적 디테일, 감정과 연결된 묘사, 독자 몰입"
            },
            "pov": {
                "focus": "시점 기법",
                "exercise": "같은 사건을 1인칭, 3인칭, 전지적 관점으로 각각 써보기",
                "tips": "각 시점의 장단점, 독자와의 거리감, 정보 전달 방식"
            },
            "pacing": {
                "focus": "속도 조절",
                "exercise": "긴장감 있는 장면과 여유로운 장면 대비",
                "tips": "문장 길이 조절, 리듬감, 독자의 호흡 고려"
            }
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
        
        return f"""당신은 출간 경험이 풍부한 전문 편집자입니다. 작가의 실제 프로젝트 완성을 도와주세요.

사용자 요청: {user_message}

**프로젝트 완성 전략:**

🎯 **목표 설정:**
- 구체적인 완성 목표 (분량, 기한, 독자층)
- 현실적인 단계별 계획
- 품질 기준 설정

📋 **실행 방법:**
1. 현재 프로젝트의 강점과 약점 분석
2. 개선이 필요한 구체적 부분 파악
3. 단계별 수정 및 보완 계획
4. 독자 반응을 고려한 최종 점검

💼 **출간 준비:**
- 장르별 시장 트렌드 고려
- 독자층에 맞는 스타일 조정
- 완성도 높은 최종 편집

**실무 조언:**
- 완벽하지 않아도 일단 완성하기
- 피드백 받을 수 있는 채널 만들기
- 꾸준한 수정과 개선

전문 편집자 관점에서 실용적이고 구체적인 조언을 제공하세요."""
    
    async def handle_request(self, user_message: str, history: Optional[List[Dict]] = None) -> Dict:
        """사용자 요청 처리 - Jane Friedman 3단계 방법론 적용"""
        
        intent, level = self.detect_intent_and_level(user_message)
        
        # 인사/무의미한 입력 처리
        if intent == "greeting":
            return await self.handle_greeting(user_message)

        # 웹 검색 의도 처리
        if intent == "web_search":
            logger.info("🌐 웹 검색 의도 감지됨. 검색을 수행합니다.")
            try:
                search_result = await self.web_search_handler.search(
                    query=user_message,
                    source='web',
                    num_results=5,
                    include_summary=True
                )
                
                summary = search_result.get("summary", "검색 결과를 요약하는 데 실패했습니다.")
                results = search_result.get("results", [])
                
                response_content = f"**🔍 웹 검색 결과 요약**\n{summary}\n\n"
                
                if results:
                    response_content += "**자세히 보기:**\n"
                    for i, res in enumerate(results[:3]):
                        response_content += f"{i+1}. [{res.get('title', '결과')}]({res.get('url', '#')})\n"
                
                return {
                    "response": response_content,
                    "cost": search_result.get("cost", 0),
                    "tokens": search_result.get("tokens", 0),
                    "model": search_result.get("model", "web_search")
                }

            except Exception as e:
                logger.error(f"웹 검색 중 오류 발생: {e}")
                return {"response": "웹 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}

        # Jane Friedman 3단계 방법론 적용
        if intent == "creation":
            return await self.generate_story_by_level(user_message, level)
        elif intent == "technique":
            prompt = self.create_technique_focused_prompt(user_message, "dialogue")
        elif "프로젝트" in user_message or "완성" in user_message or level == "advanced":
            prompt = self.create_project_application_prompt(user_message)
        else:
            prompt = self.create_practice_prompt(user_message, level)

        # 일반 응답 생성
        return await self.generate_response(prompt, intent, level)

    async def handle_greeting(self, user_message: str) -> Dict:
        """인사 및 무의미한 입력 처리"""
        
        greeting_responses = [
            "안녕하세요! 👋 Loop AI입니다. 어떤 이야기를 함께 만들어볼까요?",
            "반갑습니다! ✨ 창작에 관해 무엇이든 도와드릴게요.",
            "안녕하세요! 📚 오늘은 어떤 창작 활동을 해보실건가요?",
            "환영합니다! 🎭 상상력을 현실로 만들어보세요."
        ]
        
        response = random.choice(greeting_responses)
        
        # 작가 레벨별 맞춤 안내
        guide_message = """
**💡 이런 것들을 도와드릴 수 있어요:**

🌱 **초보 작가님:**
- "간단한 이야기 써줘" 
- "글쓰기 연습 방법 알려줘"
- "캐릭터 만드는 법 가르쳐줘"

🌿 **중급 작가님:**
- "대화 기법 연습하고 싶어"
- "묘사 실력 늘리는 방법"
- "다양한 시점으로 써보기"

🌳 **고급 작가님:**
- "내 소설 프로젝트 완성하기"
- "출간 준비 조언"
- "독자층 분석 도움"

편하게 말씀해주세요! 😊
"""
        
        return {
            "response": response + "\n\n" + guide_message,
            "cost": 0,
            "tokens": 0,
            "model": "greeting"
        }

    async def generate_story_by_level(self, user_message: str, level: str, max_tokens: int = 4000, 
                                     is_long_form: bool = False, continue_story: bool = False) -> Dict:
        """작가 레벨에 따른 맞춤형 스토리 생성"""
        
        style, length = self.extract_style_and_length(user_message)
        
        # 긴 텍스트 모드일 때 토큰 수 조정
        if is_long_form:
            # 소설 모드: 더 많은 토큰 할당
            if level == "beginner":
                target_tokens = min(max_tokens, 2000)
            elif level == "intermediate":
                target_tokens = min(max_tokens, 3000)
            else:  # advanced
                target_tokens = min(max_tokens, 4000)
        else:
            # 일반 모드: 기본 토큰 수
            if level == "beginner":
                target_tokens = 800
            elif level == "intermediate":
                target_tokens = 1200
            else:  # advanced
                target_tokens = 2000

        # 레벨별 프롬프트 전략
        if level == "beginner":
            prompt = self.create_beginner_story_prompt(user_message, style, length, is_long_form, continue_story)
            temperature = 0.7  # 안정적
        elif level == "intermediate":
            prompt = self.create_intermediate_story_prompt(user_message, style, length, is_long_form, continue_story)
            temperature = 0.8  # 약간 창의적
        else:  # advanced
            prompt = self.create_advanced_story_prompt(user_message, style, length, is_long_form, continue_story)
            temperature = 0.9  # 매우 창의적
        
        try:
            if not self.client:
                return {"response": "OpenAI 클라이언트가 설정되지 않았습니다."}

            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"당신은 {level} 레벨 작가를 위한 전문 멘토입니다. 실용적이고 도움이 되는 조언을 제공하세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="gpt-4o-mini",
                temperature=temperature,
                max_tokens=target_tokens,
                presence_penalty=0.2,
                frequency_penalty=0.3
            )
            
            response = chat_completion.choices[0].message.content or ""
            
            # 비용 및 토큰 계산
            cost = 0
            tokens = 0
            if chat_completion.usage:
                cost = (chat_completion.usage.prompt_tokens * 0.00000015) + (chat_completion.usage.completion_tokens * 0.0000006)
                tokens = chat_completion.usage.prompt_tokens + chat_completion.usage.completion_tokens
            
            return {
                "response": response,
                "cost": cost,
                "tokens": tokens,
                "model": "gpt-4o-mini",
                "level": level,
                "style": style,
                "length": length
            }
            
        except Exception as e:
            logger.error(f"레벨별 스토리 생성 오류: {e}")
            return {"response": f"스토리 생성 중 오류가 발생했습니다: {e}"}

    def create_beginner_story_prompt(self, user_message: str, style: str, length: str, 
                                    is_long_form: bool = False, continue_story: bool = False) -> str:
        """초보자용 스토리 프롬프트 - 간단하고 명확하게"""
        
        mode_instruction = ""
        if is_long_form:
            mode_instruction = """
**📖 긴 소설 모드 활성화**
- 더 풍부한 묘사와 세부사항 포함
- 캐릭터의 내면 심리 깊이 있게 표현
- 장면 전환과 분위기 조성에 신경 써서 작성
- 독자가 몰입할 수 있는 긴 호흡의 이야기
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

**초보자 맞춤 접근:**
1. 간단하고 명확한 구조 (시작-중간-끝)
2. 이해하기 쉬운 캐릭터와 상황
3. 너무 복잡하지 않은 전개
4. 완성의 성취감을 느낄 수 있는 분량

**토큰 절약 전략:**
- 핵심 내용에 집중하여 불필요한 반복 피하기
- 간결하면서도 임팩트 있는 표현 사용
- 효율적인 문장 구조로 정보 밀도 높이기

**작성 후 추가 제공:**
- 이 이야기에서 잘된 점 3가지
- 다음에 시도해볼 만한 연습 제안
- 격려 메시지

친근하고 격려하는 톤으로 써주세요."""

    def create_intermediate_story_prompt(self, user_message: str, style: str, length: str,
                                        is_long_form: bool = False, continue_story: bool = False) -> str:
        """중급자용 스토리 프롬프트 - 기법 연습 중심"""
        
        techniques = ["대화 기법", "시점 변화", "복선 설치", "캐릭터 내면 묘사", "분위기 조성"]
        focus_technique = random.choice(techniques)
        
        return f"""당신은 중급 작가의 기법 향상을 돕는 전문 코치입니다.

**요청:** {user_message}
**스타일:** {style}
**길이:** {length}
**이번 연습 기법:** {focus_technique}

**중급자 도전 과제:**
1. {focus_technique}에 특별히 집중하여 작성
2. 같은 장면을 다른 방식으로도 써보기
3. 독자의 감정을 의도적으로 조작하기
4. 예상치 못한 요소 하나 포함하기

**작성 후 분석:**
- {focus_technique} 적용 분석
- 개선 가능한 부분 구체적 지적
- 다음 단계 연습 제안

전문적이면서 실용적인 조언을 제공하세요."""

    def create_advanced_story_prompt(self, user_message: str, style: str, length: str,
                                    is_long_form: bool = False, continue_story: bool = False) -> str:
        """고급자용 스토리 프롬프트 - 완성도와 독창성 중심"""
        
        return f"""당신은 출간 경험이 풍부한 전문 작가 동료입니다.

**요청:** {user_message}
**스타일:** {style}
**길이:** {length}

**고급자 완성도 기준:**
1. 출간 가능한 수준의 완성도
2. 독창적이면서도 독자에게 어필하는 균형
3. 장르 관습을 이해하면서도 새로운 시도
4. 깊이 있는 주제 의식과 메시지

**전문가 피드백:**
- 상업적 가능성 평가
- 독자층 분석 및 마케팅 포인트
- 문학적 가치와 대중성 균형
- 시리즈 확장 가능성

동료 작가로서 솔직하고 건설적인 피드백을 주세요."""

    def extract_style_and_length(self, user_message: str) -> tuple:
        """스타일과 길이 추출"""
        
        # 스타일 감지
        style_keywords = {
            "판타지": ["판타지", "마법", "용", "마법사", "엘프"],
            "SF": ["SF", "우주", "로봇", "미래", "시간여행"],
            "로맨스": ["로맨스", "사랑", "연애", "로맨틱"],
            "스릴러": ["스릴러", "추리", "범죄", "미스터리"],
            "코미디": ["코미디", "웃긴", "유머", "재미있는"],
            "드라마": ["드라마", "감동", "현실", "일상"]
        }
        
        detected_style = "자유"
        for style, keywords in style_keywords.items():
            if any(keyword in user_message for keyword in keywords):
                detected_style = style
                break
        
        # 길이 감지
        length_keywords = {
            "짧은": ["짧은", "간단한", "짧게", "요약"],
            "긴": ["긴", "자세한", "길게", "상세한"],
            "중간": ["중간", "적당한", "보통"]
        }
        
        detected_length = "중간"
        for length, keywords in length_keywords.items():
            if any(keyword in user_message for keyword in keywords):
                detected_length = length
                break
        
        return detected_style, detected_length

    async def generate_response(self, prompt: str, intent: str, level: str) -> Dict:
        """일반 응답 생성"""
        
        try:
            if not self.client:
                return {"response": "OpenAI 클라이언트가 설정되지 않았습니다."}

            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"당신은 {level} 레벨의 작가를 돕는 전문 멘토입니다. Jane Friedman의 3단계 방법론을 따라 실용적인 도움을 제공하세요."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=1500,
                presence_penalty=0.2,
                frequency_penalty=0.3
            )
            
            response = chat_completion.choices[0].message.content or ""
            
            # 비용 및 토큰 계산
            cost = 0
            tokens = 0
            if chat_completion.usage:
                cost = (chat_completion.usage.prompt_tokens * 0.00000015) + (chat_completion.usage.completion_tokens * 0.0000006)
                tokens = chat_completion.usage.prompt_tokens + chat_completion.usage.completion_tokens
            
            return {
                "response": response,
                "cost": cost,
                "tokens": tokens,
                "model": "gpt-4o-mini",
                "intent": intent,
                "level": level
            }
            
        except Exception as e:
            logger.error(f"응답 생성 오류: {e}")
            return {"response": f"응답 생성 중 오류가 발생했습니다: {e}"}

    def test_intent_detection(self) -> Dict:
        """의도 감지 테스트 케이스"""
        
        test_cases = [
            # 인사/무의미한 입력
            ("ㅎㅇㅎㅇ", "greeting"),
            ("ㅋㅋㅋ", "greeting"),
            ("안녕", "greeting"),
            ("hi", "greeting"),
            ("123", "greeting"),
            
            # 명확한 창작 요청
            ("판타지 이야기 만들어줘", "creation"),
            ("로맨스 소설 써줘", "creation"),
            ("스토리 생성해", "creation"),
            ("이야기 창작해", "creation"),
            
            # 시놉시스 요청
            ("시놉시스 써줘", "synopsis"),
            ("줄거리 만들어", "synopsis"),
            ("요약해", "synopsis"),
            
            # 웹 검색
            ("최신 뉴스 알려줘", "web_search"),
            ("날씨 어때", "web_search"),
            ("영화 순위 찾아줘", "web_search"),
            
            # 일반 질문
            ("창작 팁 알려줘", "general"),
            ("어떻게 써야 할까", "general"),
        ]
        
        results = {}
        for test_input, expected in test_cases:
            detected = self.detect_intent_and_level(test_input)
            results[test_input] = {
                "expected": expected,
                "detected": detected,
                "correct": detected == expected
            }
        
        accuracy = sum(1 for r in results.values() if r["correct"]) / len(results)
        
        return {
            "accuracy": accuracy,
            "total_tests": len(test_cases),
            "results": results
        }

    def get_prompt_stats(self, prompt: str) -> Dict:
        """프롬프트 통계 정보"""
        
        import re
        
        # 기본 통계
        char_count = len(prompt)
        word_count = len(prompt.split())
        line_count = len(prompt.split('\n'))
        
        # 토큰 추정 (한국어 기준)
        estimated_tokens = char_count // 3  # 한국어는 대략 3글자당 1토큰
        
        # 구조 분석
        has_xml_tags = bool(re.search(r'<[^>]+>', prompt))
        has_markdown = bool(re.search(r'[#*`]', prompt))
        has_instructions = "지침" in prompt or "instruction" in prompt.lower()
        
        return {
            "char_count": char_count,
            "word_count": word_count,
            "line_count": line_count,
            "estimated_tokens": estimated_tokens,
            "has_xml_tags": has_xml_tags,
            "has_markdown": has_markdown,
            "has_instructions": has_instructions,
            "prompt_style": "claude" if has_xml_tags else "gpt"
        } 