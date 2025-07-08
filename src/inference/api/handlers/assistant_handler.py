"""
Loop AI 글쓰기 지원 기능 핸들러
- 스마트 문장 개선
- (추후 확장될 기능들)
"""
import logging
import re
from typing import cast

from openai import AsyncOpenAI

from src.shared.prompts.loader import get_prompt, load_prompts_config
from .web_search_handler import WebSearchHandler
from ..shared_types import (
    ImproveSentenceResult,
    SmartSentenceImprovementResult,
    PlotHoleDetectionResult,
    CharacterConsistencyResult,
    CliffhangerSuggestion,
    CliffhangerGenerationResult,
    ReaderResponseResult,
    EpisodeLengthResult,
    BetaReadResult,
    TrendAnalysisResult
)

logger = logging.getLogger(__name__)


class AssistantHandler:
    """글쓰기 지원 도구를 관리하는 핸들러"""

    client: AsyncOpenAI | None  # 명시적 클래스 속성 타입 애노테이션
    web_search_handler: WebSearchHandler | None  # 명시적 클래스 속성 타입 애노테이션

    def __init__(self, openai_client: AsyncOpenAI | None = None, web_search_handler: WebSearchHandler | None = None):
        """
        핸들러 초기화
        Args:
            openai_client: AsyncOpenAI 클라이언트 인스턴스
            web_search_handler: WebSearchHandler 클라이언트 인스턴스
        """
        self.client = openai_client
        self.web_search_handler = web_search_handler
        logger.info("✅ AssistantHandler 초기화 완료")

    async def improve_sentence(
        self,
        original_sentence: str,
        genre: str,
        character_profile: str,
        context: str,
        model: str | None = None,
    ) -> ImproveSentenceResult:
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

    async def run_smart_sentence_improvement(
        self,
        original_text: str,
        model: str | None = None,
    ) -> SmartSentenceImprovementResult:
        """
        AI를 사용하여 문장을 개선하고 여러 대안을 제시합니다.
        새로운 smart_sentence_improvement 프롬프트를 사용합니다.
        """
        if not self.client:
            logger.error("❌ OpenAI 클라이언트가 초기화되지 않았습니다.")
            raise ValueError("OpenAI client is not initialized")

        try:
            # load prompts configuration and cast to object-keyed dict
            prompts_config = cast(dict[str, object], load_prompts_config())
            raw_prompts = prompts_config.get("prompts")
            prompts_list: list[dict[str, object]] = cast(list[dict[str, object]], raw_prompts) if isinstance(raw_prompts, list) else []
            # default empty template data for fallback
            default_pt_data: dict[str, object] = {}
            prompt_template_data: dict[str, object] = next(
                (p for p in prompts_list if p.get("name") == "smart_sentence_improvement"),
                default_pt_data
            )
            if not prompt_template_data:
                raise ValueError("smart_sentence_improvement 프롬프트 데이터를 찾을 수 없습니다.")

            # validate and assign template and persona
            template_obj = prompt_template_data.get("template")
            if not isinstance(template_obj, str):
                raise ValueError("smart_sentence_improvement 프롬프트 데이터를 찾을 수 없습니다.")
            persona_obj = prompt_template_data.get("persona")
            prompt_template: str = template_obj
            persona: str = persona_obj if isinstance(persona_obj, str) else template_obj

            prompt_content: str = prompt_template.format(user_message=original_text)
            
            selected_model = model or "gpt-4o-mini"

            api_response = await self.client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": prompt_content}
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            content = api_response.choices[0].message.content
            if not content:
                raise ValueError("API 응답이 비어있습니다.")

            prompt_tokens = api_response.usage.prompt_tokens if api_response.usage else 0
            completion_tokens = api_response.usage.completion_tokens if api_response.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            cost = total_tokens * (0.00015 / 1000)

            return {
                "improvement_suggestions": content,
                "model": selected_model,
                "cost": cost,
                "tokens": total_tokens,
            }
        except Exception as e:
            logger.error(f"❌ 스마트 문장 개선 중 오류 발생: {e}")
            raise

    async def detect_plot_holes(
        self,
        full_story_text: str,
        model: str | None = None,
    ) -> PlotHoleDetectionResult:
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
    ) -> CharacterConsistencyResult:
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
    ) -> CliffhangerGenerationResult:
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

    def _parse_cliffhanger_suggestions(self, content: str) -> list[CliffhangerSuggestion]:
        """
        AI 응답에서 클리프행어 제안들을 파싱합니다.
        - 제안: ...
        """
        suggestions: list[CliffhangerSuggestion] = []  # annotated list for Pyright
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
    ) -> ReaderResponseResult:
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
            parsed_response = self._parse_reader_response(content)

            prompt_tokens = api_response.usage.prompt_tokens if api_response.usage else 0
            completion_tokens = api_response.usage.completion_tokens if api_response.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            cost = total_tokens * (0.005 / 1000)

            return {
                "prediction_report": parsed_response,
                "model": selected_model,
                "cost": cost,
                "tokens": total_tokens,
            }

        except Exception as e:
            logger.error(f"❌ 독자 반응 예측 중 오류 발생: {e}")
            raise

    def _parse_reader_response(self, content: str) -> dict[str, str | float]:
        """독자 반응 예측 결과를 파싱합니다."""
        try:
            # 각 섹션별로 내용을 추출
            positive_reactions_match = re.search(r"\*\*긍정적 반응 \(Positive Reactions\):\*\*\n(.*?)(?=\n\*\*|\Z)", content, re.DOTALL)
            potential_criticisms_match = re.search(r"\*\*잠재적 비판 \(Potential Criticisms\):\*\*\n(.*?)(?=\n\*\*|\Z)", content, re.DOTALL)
            tip_match = re.search(r"\*\*참여 극대화를 위한 팁 \(Tip to Maximize Engagement\):\*\*\n(.*?)(?=\n\*\*|\Z)", content, re.DOTALL)

            return {
                "positive_reactions": positive_reactions_match.group(1).strip() if positive_reactions_match else "파싱 실패",
                "potential_criticisms": potential_criticisms_match.group(1).strip() if potential_criticisms_match else "파싱 실패",
                "tip": tip_match.group(1).strip() if tip_match else "파싱 실패",
            }
        except Exception as e:
            logger.error(f"독자 반응 파싱 중 오류 발생: {e}")
            return {
                "positive_reactions": "파싱 중 오류 발생",
                "potential_criticisms": "파싱 중 오류 발생",
                "tip": "파싱 중 오류 발생",
            }

    async def optimize_episode_length(
        self,
        episode_text: str,
        platform: str,
        model: str | None = None,
    ) -> EpisodeLengthResult:
        """
        AI를 사용하여 웹소설 에피소드의 길이를 최적화하고 분할 지점을 제안합니다.
        """
        if not self.client:
            logger.error("❌ OpenAI 클라이언트가 초기화되지 않았습니다.")
            raise ValueError("OpenAI client is not initialized")

        try:
            prompt_template = get_prompt("episode_length_optimizer")
            if not prompt_template:
                raise ValueError("episode_length_optimizer 템플릿을 찾을 수 없습니다.")

            prompt = prompt_template.format(episode_text=episode_text, platform=platform)
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
            cost = total_tokens * (0.005 / 1000) # gpt-4o 기준 단순 계산

            # 파싱 로직 추가
            parsed_report = self._parse_optimization_result(content)

            return {
                "optimization_report": parsed_report,
                "model": selected_model,
                "cost": cost,
                "tokens": total_tokens,
            }

        except Exception as e:
            logger.error(f"❌ 에피소드 길이 최적화 중 오류 발생: {e}")
            raise

    def _parse_optimization_result(self, content: str) -> dict[str, object]:
        """에피소드 길이 최적화 결과를 파싱합니다."""
        try:
            recommendation_match = re.search(r"\*\*Overall Recommendation:\*\*\n(.*?)(?=\n\*\*Detailed Split Points:\*\*|\Z)", content, re.DOTALL)
            
            split_points: list[dict[str, object]] = []  # annotated for Pyright
            # Detailed Split Points 섹션 전체를 가져옴
            split_points_section_match = re.search(r"\*\*Detailed Split Points:\*\*(.*?)(\*\*Monetization Tip:\*\*|\Z)", content, re.DOTALL)
            if split_points_section_match:
                split_points_text = split_points_section_match.group(1).strip()
                # 각 에피소드 종료 지점을 찾음
                episode_matches = re.finditer(r"-\s\*\*Episode\s(\d+)\sEnd:\*\*\s(.*?)\(Reason:\s(.*?)\)", split_points_text, re.DOTALL)
                for match in episode_matches:
                    split_points.append({
                        "episode": int(match.group(1)),
                        "ending_text": match.group(2).strip(),
                        "reason": match.group(3).strip().rstrip(')')
                    })

            tip_match = re.search(r"\*\*Monetization Tip:\*\*\n(.*?)(?=\Z)", content, re.DOTALL)

            return {
                "recommendation": recommendation_match.group(1).strip() if recommendation_match else "파싱 실패",
                "split_points": split_points,
                "monetization_tip": tip_match.group(1).strip() if tip_match else "파싱 실패"
            }
        except Exception as e:
            logger.error(f"에피소드 최적화 결과 파싱 중 오류 발생: {e}")
            return {"error": "파싱 중 오류가 발생했습니다.", "details": str(e)}

    async def get_beta_read_feedback(
        self,
        manuscript: str,
        genre: str,
        target_audience: str,
        author_concerns: str | None = None,
        model: str | None = None,
    ) -> BetaReadResult:
        """
        AI 베타리더를 통해 원고에 대한 종합적인 피드백을 받습니다.
        """
        if not self.client:
            logger.error("❌ OpenAI 클라이언트가 초기화되지 않았습니다.")
            raise ValueError("OpenAI client is not initialized")

        try:
            prompt_template = get_prompt("ai_beta_reader")
            if not prompt_template:
                raise ValueError("ai_beta_reader 템플릿을 찾을 수 없습니다.")

            prompt = prompt_template.format(
                manuscript=manuscript,
                genre=genre,
                target_audience=target_audience,
                author_concerns=author_concerns or "특별한 우려 사항 없음",
            )
            selected_model = model or "gpt-4o"  # 종합 분석을 위해 gpt-4o 기본 사용

            api_response = await self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.4,
                max_tokens=3500, # 상세한 보고서를 위해 토큰 넉넉하게 설정
            )

            content = api_response.choices[0].message.content
            if not content:
                raise ValueError("API 응답이 비어있습니다.")

            prompt_tokens = api_response.usage.prompt_tokens if api_response.usage else 0
            completion_tokens = api_response.usage.completion_tokens if api_response.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            cost = total_tokens * (0.005 / 1000)

            # 파싱 로직 추가
            parsed_report = self._parse_beta_read_report(content)

            return {
                "beta_read_report": parsed_report,
                "model": selected_model,
                "cost": cost,
                "tokens": total_tokens,
            }

        except Exception as e:
            logger.error(f"❌ AI 베타리딩 중 오류 발생: {e}")
            raise

    def _parse_beta_read_report(self, content: str) -> dict[str, object]:
        """AI 베타리더의 리포트를 파싱합니다."""
        try:
            report: dict[str, object] = {"raw_text": content}  # annotated for Pyright
            
            # Executive Summary 파싱
            summary_match = re.search(r"\*\*Executive Summary \(Overall Score: (\d+)/100\)\*\*\n(.*?)(?=\n---\n|\Z)", content, re.DOTALL)
            if summary_match:
                report["overall_score"] = int(summary_match.group(1))
                report["executive_summary"] = summary_match.group(2).strip()

            # 5가지 분석 항목 파싱
            dimensions = ["Pacing and Flow", "Plot and Structure", "Characterization", "Immersion and World-Building", "Reader Engagement (Hook)"]
            report["detailed_analysis"] = {}
            for dim in dimensions:
                pattern = rf"\*\*{re.escape(dim)} \(Score: (\d+)/100\)\*\*(.*?)(?=\n\*\*|\n---\n\*\*Final Recommendation\*\*|\Z)"
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    dim_key = dim.lower().replace(" ", "_").replace("(", "").replace(")", "")
                    dim_content = match.group(2).strip()
                    
                    strengths_match = re.search(r"\*\*Strengths:\*\*(.*?)(?=\n\*\*Areas for Improvement:\*\*|\Z)", dim_content, re.DOTALL)
                    improvements_match = re.search(r"\*\*Areas for Improvement:\*\*(.*?)(?=\n\*\*Actionable Suggestion:\*\*|\Z)", dim_content, re.DOTALL)
                    suggestion_match = re.search(r"\*\*Actionable Suggestion:\*\*(.*?)$", dim_content, re.DOTALL)
                    
                    report["detailed_analysis"][dim_key] = {
                        "score": int(match.group(1)),
                        "strengths": strengths_match.group(1).strip() if strengths_match else "",
                        "improvements": improvements_match.group(1).strip() if improvements_match else "",
                        "suggestion": suggestion_match.group(1).strip() if suggestion_match else ""
                    }
            
            # Final Recommendation 파싱
            recommendation_match = re.search(r"\*\*Final Recommendation:\*\*\n(.*?)$", content, re.DOTALL)
            if recommendation_match:
                report["final_recommendation"] = recommendation_match.group(1).strip()

            return report
        except Exception as e:
            logger.error(f"AI 베타리포트 파싱 중 오류 발생: {e}")
            return {"error": "파싱 중 오류가 발생했습니다.", "raw_text": content}

    async def analyze_trends(
        self,
        genre: str,
        synopsis: str,
        keywords: list[str],
        platform: str,
        model: str | None = None,
    ) -> TrendAnalysisResult:
        """
        웹 검색을 통해 최신 트렌드를 분석하고, 작가의 작품에 적용할 아이디어를 제안합니다.
        """
        if not self.client or not self.web_search_handler:
            raise ValueError("OpenAI 또는 WebSearch 클라이언트가 초기화되지 않았습니다.")

        try:
            # 1. 웹 검색 수행
            search_query = f"{platform} 웹소설 최신 인기 순위 {genre} 트렌드"
            logger.info(f"수행할 웹 검색 쿼리: {search_query}")
            
            _summary, search_results = await self.web_search_handler.search(
                query=search_query,
                source="web",
                num_results=5,
                include_summary=False # 개별 요약이 아닌 전체 분석을 위해 False
            )
            
            # 검색 결과 텍스트로 변환
            search_data = "\n".join(
                [f"- Title: {res['title']}\n  Snippet: {res['snippet']}" for res in search_results]
            )

            # 2. AI 분석 요청
            prompt_template = get_prompt("trend_analyzer")
            if not prompt_template:
                raise ValueError("trend_analyzer 템플릿을 찾을 수 없습니다.")

            prompt = prompt_template.format(
                genre=genre,
                synopsis=synopsis,
                keywords=", ".join(keywords),
                platform=platform,
                web_search_data=search_data,
            )
            selected_model = model or "gpt-4o"

            api_response = await self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.5,
                max_tokens=2500,
            )

            content = api_response.choices[0].message.content
            if not content:
                raise ValueError("API 응답이 비어있습니다.")

            prompt_tokens = api_response.usage.prompt_tokens if api_response.usage else 0
            completion_tokens = api_response.usage.completion_tokens if api_response.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            cost = total_tokens * (0.005 / 1000)

            return {
                "trend_report": content, # 파싱은 추후 추가하거나 프론트에서 직접 처리
                "model": selected_model,
                "cost": cost,
                "tokens": total_tokens,
                "searched_data": search_results # 어떤 데이터를 기반으로 분석했는지 전달
            }

        except Exception as e:
            logger.error(f"❌ 트렌드 분석 중 오류 발생: {e}")
            raise 