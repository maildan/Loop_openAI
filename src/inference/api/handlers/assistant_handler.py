"""
Loop AI 글쓰기 지원 기능 핸들러
- 스마트 문장 개선
- (추후 확장될 기능들)
"""
import logging
import re
from typing import Any

from openai import AsyncOpenAI

from src.shared.prompts.loader import get_prompt

logger = logging.getLogger(__name__)


class AssistantHandler:
    """글쓰기 지원 도구를 관리하는 핸들러"""

    def __init__(self, openai_client: AsyncOpenAI | None = None):
        """
        핸들러 초기화
        Args:
            openai_client: AsyncOpenAI 클라이언트 인스턴스
        """
        self.client = openai_client
        logger.info("✅ AssistantHandler 초기화 완료")

    async def improve_sentence(
        self,
        original_sentence: str,
        genre: str,
        character_profile: str,
        context: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        AI를 사용하여 문장을 3가지 버전으로 개선합니다.
        1. 더 생생한 묘사
        2. 더 간결하고 힘있게
        3. 캐릭터의 목소리로
        """
        if not self.client:
            logger.error("❌ OpenAI 클라이언트가 초기화되지 않았습니다.")
            raise ValueError("OpenAI client is not initialized")

        try:
            prompt_template = get_prompt("sentence_improvement")
            if not prompt_template:
                raise ValueError("sentence_improvement 템플릿을 찾을 수 없습니다.")

            prompt = prompt_template.format(
                genre=genre,
                character_profile=character_profile,
                context=context,
                original_sentence=original_sentence,
            )

            selected_model = model or "gpt-4o-mini"

            api_response = await self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7,
                max_tokens=1500,
            )

            content = api_response.choices[0].message.content
            if not content:
                raise ValueError("API 응답이 비어있습니다.")

            # 응답 파싱
            vivid = self._parse_response_section(content, "1")
            concise = self._parse_response_section(content, "2")
            character = self._parse_response_section(content, "3")

            # 토큰 및 비용 계산 (실제 구현에서는 calculate_cost 함수를 사용해야 함)
            prompt_tokens = api_response.usage.prompt_tokens if api_response.usage else 0
            completion_tokens = api_response.usage.completion_tokens if api_response.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            
            # 비용 계산 로직은 server.py에 있으므로 여기서는 단순화
            cost = total_tokens * (0.00015 / 1000) # gpt-4o-mini 기준 단순 계산

            return {
                "vivid_sentence": vivid,
                "concise_sentence": concise,
                "character_voice_sentence": character,
                "model": selected_model,
                "cost": cost,
                "tokens": total_tokens,
            }

        except Exception as e:
            logger.error(f"❌ 문장 개선 중 오류 발생: {e}")
            raise

    def _parse_response_section(self, content: str, section_number: str) -> str:
        """
        정규표현식을 사용하여 응답 내용에서 특정 섹션의 텍스트를 추출합니다.
        예: `**1. 더 생생한 묘사 버전 (Vivid Description):**` 다음의 텍스트를 추출
        """
        pattern = rf"\*\*{section_number}\..*?\*\*\n(.*?)(?=\n\*\*|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # 패턴 매칭 실패 시 대체 로직
        # 간단한 분할을 시도
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith(f"**{section_number}."):
                if i + 1 < len(lines):
                    return '\n'.join(lines[i+1:]).split('**')[0].strip()

        logger.warning(f"⚠️ 섹션 {section_number}의 내용을 파싱하지 못했습니다.")
        return "파싱에 실패했습니다. AI 응답 형식을 확인해주세요."

    async def detect_plot_holes(
        self,
        full_story_text: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        AI를 사용하여 이야기의 플롯 홀을 감지합니다.
        """
        if not self.client:
            logger.error("❌ OpenAI 클라이언트가 초기화되지 않았습니다.")
            raise ValueError("OpenAI client is not initialized")

        try:
            prompt_template = get_prompt("plot_hole_detector")
            if not prompt_template:
                raise ValueError("plot_hole_detector 템플릿을 찾을 수 없습니다.")

            prompt = prompt_template.format(full_story_text=full_story_text)
            selected_model = model or "gpt-4o"  # 더 긴 컨텍스트와 분석을 위해 gpt-4o를 기본값으로 고려

            api_response = await self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3, # 분석 작업이므로 낮은 온도로 설정
                max_tokens=2500, # 긴 분석 결과를 위해 토큰 수 상향
            )

            content = api_response.choices[0].message.content
            if not content:
                raise ValueError("API 응답이 비어있습니다.")

            # 토큰 및 비용 계산
            prompt_tokens = api_response.usage.prompt_tokens if api_response.usage else 0
            completion_tokens = api_response.usage.completion_tokens if api_response.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            cost = total_tokens * (0.005 / 1000) # gpt-4o 기준 단순 계산

            return {
                "detection_report": content,
                "model": selected_model,
                "cost": cost,
                "tokens": total_tokens,
            }

        except Exception as e:
            logger.error(f"❌ 플롯 홀 감지 중 오류 발생: {e}")
            raise

    async def check_character_consistency(
        self,
        character_name: str,
        personality: str,
        speech_style: str,
        core_values: str,
        other_settings: str,
        story_text_for_analysis: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        AI를 사용하여 캐릭터의 일관성을 검증합니다.
        """
        if not self.client:
            logger.error("❌ OpenAI 클라이언트가 초기화되지 않았습니다.")
            raise ValueError("OpenAI client is not initialized")

        try:
            prompt_template = get_prompt("character_consistency_checker")
            if not prompt_template:
                raise ValueError("character_consistency_checker 템플릿을 찾을 수 없습니다.")

            prompt = prompt_template.format(
                character_name=character_name,
                personality=personality,
                speech_style=speech_style,
                core_values=core_values,
                other_settings=other_settings,
                story_text_for_analysis=story_text_for_analysis,
            )
            selected_model = model or "gpt-4o"

            api_response = await self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3,
                max_tokens=2000,
            )

            content = api_response.choices[0].message.content
            if not content:
                raise ValueError("API 응답이 비어있습니다.")

            prompt_tokens = api_response.usage.prompt_tokens if api_response.usage else 0
            completion_tokens = api_response.usage.completion_tokens if api_response.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            cost = total_tokens * (0.005 / 1000)

            return {
                "consistency_report": content,
                "model": selected_model,
                "cost": cost,
                "tokens": total_tokens,
            }

        except Exception as e:
            logger.error(f"❌ 캐릭터 일관성 검증 중 오류 발생: {e}")
            raise

    async def generate_cliffhanger(
        self,
        genre: str,
        scene_context: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        AI를 사용하여 주어진 장르와 장면에 맞는 클리프행어를 생성합니다.
        """
        if not self.client:
            logger.error("❌ OpenAI 클라이언트가 초기화되지 않았습니다.")
            raise ValueError("OpenAI client is not initialized")

        try:
            prompt_template = get_prompt("cliffhanger_generator")
            if not prompt_template:
                raise ValueError("cliffhanger_generator 템플릿을 찾을 수 없습니다.")

            prompt = prompt_template.format(genre=genre, scene_context=scene_context)
            selected_model = model or "gpt-4o"

            api_response = await self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7, # 창의적인 생성을 위해 온도를 약간 높임
                max_tokens=1500,
            )

            content = api_response.choices[0].message.content
            if not content:
                raise ValueError("API 응답이 비어있습니다.")

            # 결과 파싱 (향후 더 정교한 파싱 로직 추가 가능)
            suggestions = self._parse_cliffhanger_suggestions(content)

            prompt_tokens = api_response.usage.prompt_tokens if api_response.usage else 0
            completion_tokens = api_response.usage.completion_tokens if api_response.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            cost = total_tokens * (0.005 / 1000)

            return {
                "suggestions": suggestions,
                "model": selected_model,
                "cost": cost,
                "tokens": total_tokens,
            }

        except Exception as e:
            logger.error(f"❌ 클리프행어 생성 중 오류 발생: {e}")
            raise

    def _parse_cliffhanger_suggestions(self, content: str) -> list[dict[str, str]]:
        """
        클리프행어 생성 결과를 파싱하여 구조화된 데이터로 반환합니다.
        """
        suggestions = []
        # '타입'을 기준으로 섹션을 나눔
        sections = re.split(r'###\s*타입\s*\d+:', content)
        
        for section in sections:
            if not section.strip():
                continue

            suggestion_match = re.search(r'-\s*제안\s*:\s*(.*)', section, re.DOTALL)
            reaction_match = re.search(r'-\s*예상 독자 반응\s*:\s*(.*)', section, re.DOTALL)

            if suggestion_match and reaction_match:
                suggestion_text = suggestion_match.group(1).strip()
                reaction_text = reaction_match.group(1).strip()
                suggestions.append({
                    "suggestion": suggestion_text,
                    "expected_reaction": reaction_text,
                })
        
        # 파싱 실패 시 원본 텍스트를 그대로 반환하는 예외 처리
        if not suggestions:
            return [{"suggestion": content, "expected_reaction": "파싱 실패"}]

        return suggestions

    async def predict_reader_response(
        self,
        platform: str,
        scene_context: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        AI를 사용하여 특정 장면에 대한 독자 반응을 예측합니다.
        """
        if not self.client:
            logger.error("❌ OpenAI 클라이언트가 초기화되지 않았습니다.")
            raise ValueError("OpenAI client is not initialized")

        try:
            prompt_template = get_prompt("reader_response_predictor")
            if not prompt_template:
                raise ValueError("reader_response_predictor 템플릿을 찾을 수 없습니다.")

            prompt = prompt_template.format(platform=platform, scene_context=scene_context)
            selected_model = model or "gpt-4o"

            api_response = await self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.5,
                max_tokens=2000,
            )

            content = api_response.choices[0].message.content
            if not content:
                raise ValueError("API 응답이 비어있습니다.")

            # 결과 파싱 (향후 더 정교한 파싱 로직 추가 가능)
            parsed_report = self._parse_reader_response(content)

            prompt_tokens = api_response.usage.prompt_tokens if api_response.usage else 0
            completion_tokens = api_response.usage.completion_tokens if api_response.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            cost = total_tokens * (0.005 / 1000)

            return {
                "prediction_report": parsed_report,
                "model": selected_model,
                "cost": cost,
                "tokens": total_tokens,
            }

        except Exception as e:
            logger.error(f"❌ 독자 반응 예측 중 오류 발생: {e}")
            raise

    def _parse_reader_response(self, content: str) -> dict[str, Any]:
        """
        독자 반응 예측 결과를 파싱하여 구조화된 데이터로 반환합니다.
        """
        # 간단한 텍스트 기반 파싱, 향후 정규식 등으로 고도화 가능
        report = {"raw_text": content}
        
        # 각 섹션별로 내용을 추출하는 로직을 추가할 수 있습니다.
        # 예를 들어, "예상 댓글" 섹션만 따로 추출
        try:
            comments_section = re.search(r"예상 댓글 \(Top 3\):([\s\S]*?)이탈 위험도", content, re.DOTALL)
            if comments_section:
                report["predicted_comments"] = comments_section.group(1).strip()

            risk_section = re.search(r"이탈 위험도 \(Drop-off Risk\):([\s\S]*?)참여도 부스트", content, re.DOTALL)
            if risk_section:
                report["drop_off_risk"] = risk_section.group(1).strip()
            
            boost_section = re.search(r"참여도 부스트 \(Engagement Boost\):([\s\S]*?)전략적 개선 제안", content, re.DOTALL)
            if boost_section:
                report["engagement_boost"] = boost_section.group(1).strip()

            suggestion_section = re.search(r"전략적 개선 제안:([\s\S]*)", content, re.DOTALL)
            if suggestion_section:
                report["suggestions"] = suggestion_section.group(1).strip()

        except Exception:
             # 파싱 중 오류가 발생해도 원본 텍스트는 반환
            pass

        return report 