"""
Loop AI 맞춤법 검사 핸들러
서버의 맞춤법 검사 관련 로직을 모듈화
"""

import logging
from typing import TypedDict, cast
import sys
import os
from openai import AsyncOpenAI
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from src.utils.spellcheck import (
    get_spellchecker,
    check_spelling,
    suggest_corrections,
    correct_word,
    KoreanSpellChecker,
    FullCheckResult,
    ModuleStats,
)
from src.utils.style_analyzer import StyleAnalyzer

logger = logging.getLogger(__name__)


# --- 핸들러 전용 TypedDicts ---
class HandlerCheckResult(FullCheckResult):
    """핸들러가 추가 정보를 포함한 맞춤법 검사 결과"""

    handler: str
    dictionary_size: int


class DictionaryInfo(TypedDict):
    size: int
    source: str


class Suggestion(TypedDict):
    word: str
    confidence: int


class Recommendation(TypedDict):
    word: str
    suggestions: list[Suggestion]


class SpellcheckApiResponse(TypedDict, total=False):
    success: bool
    original_text: str
    corrected_text: str
    errors_found: int
    error_words: list[str]
    suggestions: dict[str, list[str]]
    accuracy: float
    total_words: int
    auto_corrected: bool
    dictionary_info: DictionaryInfo
    recommendations: list[Recommendation]
    error: str
    reason: str
    context_analysis: str


# TypedDict for AI 기반 문맥 교정 결과
class AICorrectionResult(TypedDict, total=False):
    corrected_text: str
    reason: str
    context_analysis: str

class SpellCheckHandler:
    """맞춤법 검사 및 문체 제안 핸들러"""

    spellchecker: KoreanSpellChecker
    style_analyzer: StyleAnalyzer
    openai_client: AsyncOpenAI | None

    def __init__(self, openai_client: AsyncOpenAI | None = None):
        """맞춤법 검사 핸들러 초기화"""
        self.spellchecker = get_spellchecker()
        self.style_analyzer = StyleAnalyzer()
        self.openai_client = openai_client
        logger.info("✅ 맞춤법 검사 및 문체 분석 핸들러 초기화 완료")

    def check_text(self, text: str) -> HandlerCheckResult:
        """
        텍스트 맞춤법 검사

        Args:
            text: 검사할 텍스트

        Returns:
            HandlerCheckResult: 맞춤법 검사 결과
        """
        try:
            result = check_spelling(text)
            stats = self.spellchecker.get_stats()

            # TypedDict는 생성 후 키를 추가할 수 없으므로, 모든 정보를 담아 새로 생성합니다.
            handler_result: HandlerCheckResult = {
                "original": result["original"],
                "corrected": result["corrected"],
                "errors": result["errors"],
                "suggestions": result["suggestions"],
                "stats": result["stats"],
                "handler": "SpellCheckHandler",
                "dictionary_size": stats.get("dictionary_size", 0),
            }
            return handler_result

        except Exception as e:
            logger.error(f"❌ 맞춤법 검사 중 오류: {e}")
            # 오류 발생 시에도 TypedDict 구조를 따릅니다.
            error_stats: FullCheckResult = {
                "original": text,
                "corrected": text,
                "errors": [],
                "suggestions": {},
                "stats": {"total_words": 0, "errors": 0, "accuracy": 100.0},
            }
            # 이 경우 'error' 키는 HandlerCheckResult에 없으므로 추가할 수 없습니다.
            # 로깅으로 충분히 처리합니다.
            return {
                **error_stats,
                "handler": "SpellCheckHandler",
                "dictionary_size": 0,
            }

    def get_word_suggestions(
        self, word: str, limit: int = 5
    ) -> list[tuple[str, int]]:
        """
        단어 수정 제안

        Args:
            word: 검사할 단어
            limit: 최대 제안 개수

        Returns:
            list[tuple[str, int]]: (제안단어, 유사도점수) 리스트
        """
        try:
            return suggest_corrections(word, limit)
        except Exception as e:
            logger.error(f"❌ 단어 제안 생성 중 오류: {e}")
            return []

    def correct_single_word(self, word: str) -> str:
        """
        단어 자동 수정

        Args:
            word: 수정할 단어

        Returns:
            str: 수정된 단어
        """
        try:
            return correct_word(word)
        except Exception as e:
            logger.error(f"❌ 단어 수정 중 오류: {e}")
            return word

    def is_word_correct(self, word: str) -> bool:
        """
        단어가 올바른 맞춤법인지 확인

        Args:
            word: 검사할 단어

        Returns:
            bool: 올바른 맞춤법이면 True
        """
        try:
            return self.spellchecker.is_correct(word)
        except Exception as e:
            logger.error(f"❌ 단어 검사 중 오류: {e}")
            return True  # 오류 시 올바른 것으로 가정

    def get_statistics(self) -> ModuleStats:
        """맞춤법 검사기 통계 정보"""
        try:
            return self.spellchecker.get_stats()
        except Exception as e:
            logger.error(f"❌ 통계 정보 조회 중 오류: {e}")
            # ModuleStats 타입에 'error'가 없으므로 반환할 수 없습니다.
            # 기본 통계 정보를 반환합니다.
            return {
                "dictionary_size": 0,
                "metadata": {"name": "error", "status": str(e)},
                "status": "error",
            }

    def batch_check(self, texts: list[str]) -> list[HandlerCheckResult]:
        """
        여러 텍스트 일괄 맞춤법 검사

        Args:
            texts: 검사할 텍스트 리스트

        Returns:
            list[HandlerCheckResult]: 각 텍스트의 검사 결과 리스트
        """
        results: list[HandlerCheckResult] = []

        for text in texts:
            result = self.check_text(text)
            results.append(result)

        return results

    def create_spellcheck_response(
        self, text: str, auto_correct: bool = True
    ) -> SpellcheckApiResponse:
        """
        맞춤법 검사 응답 생성 (API 응답용)

        Args:
            text: 검사할 텍스트
            auto_correct: 자동 수정 여부

        Returns:
            SpellcheckApiResponse: API 응답 형태의 결과
        """
        try:
            # 기본 맞춤법 검사
            check_result = self.check_text(text)
            stats = self.spellchecker.get_stats()
            metadata = stats.get("metadata", {})

            # 추가 정보 생성
            response: SpellcheckApiResponse = {
                "success": True,
                "original_text": text,
                # corrected may be empty string; fallback to original text
                "corrected_text": (check_result["corrected"] if auto_correct and check_result["corrected"] else text),
                "errors_found": len(check_result["errors"]),
                "error_words": check_result["errors"],
                "suggestions": check_result["suggestions"],
                "accuracy": check_result["stats"]["accuracy"],
                "total_words": check_result["stats"]["total_words"],
                "auto_corrected": auto_correct,
                "dictionary_info": {
                    "size": stats.get("dictionary_size", -1),
                    "source": metadata.get("name", "알 수 없음"),
                },
            }

            # 권장사항 추가
            if check_result["errors"]:
                recommendations: list[Recommendation] = []
                for error_word in check_result["errors"][:3]:  # 상위 3개만
                    suggestions = self.get_word_suggestions(error_word, 3)
                    if suggestions:
                        recommendations.append(
                            {
                                "word": error_word,
                                "suggestions": [
                                    {"word": s[0], "confidence": s[1]}
                                    for s in suggestions
                                ],
                            }
                        )
                if recommendations:
                    response["recommendations"] = recommendations

            return response

        except Exception as e:
            logger.error(f"❌ 맞춤법 검사 응답 생성 중 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_text": text,
            }

    async def context_aware_correction(
        self, target_text: str, full_document: str
    ) -> SpellcheckApiResponse:
        """
        AI를 사용하여 문맥을 고려한 맞춤법 및 문체 교정을 수행합니다.

        Args:
            target_text: 교정할 대상 텍스트
            full_document: 전체 문서 (문맥 파악용)

        Returns:
            SpellcheckApiResponse: AI 교정 결과가 포함된 API 응답
        """
        if not self.openai_client:
            logger.warning(
                "⚠️ OpenAI 클라이언트가 설정되지 않아 AI 기반 교정을 건너뜁니다."
            )
            return {
                "success": False,
                "error": "OpenAI client not configured",
                "original_text": target_text,
                "corrected_text": target_text,
                "errors_found": -1,
                "error_words": [],
                "accuracy": 100.0,
                "total_words": len(target_text.split()),
            }

        try:
            # 더 정교한 프롬프트
            prompt = f"""당신은 한국어 글쓰기 전문가입니다. 다음은 사용자가 작성한 전체 문서의 일부입니다.
전체 문맥을 파악하여, 사용자가 교정을 요청한 특정 부분의 맞춤법과 문체를 자연스럽게 수정해주세요.

[전체 문서]
{full_document}

[교정 대상 문장]
{target_text}

수정된 문장과 그 이유를 JSON 형식으로 응답해주세요.
형식: {{"corrected_text": "수정된 문장", "reason": "수정 이유", "context_analysis": "문맥 분석 결과"}}
"""
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            if response.choices[0].message.content:
                # JSON -> dict[str, object] -> TypedDict로 캐스팅
                ai_raw = cast(dict[str, object], json.loads(response.choices[0].message.content))
                ai_result = cast(AICorrectionResult, cast(object, ai_raw))

                # 키 존재 여부 검사 후 값 획득 (TypedDict 안정성 확보)
                corrected = ai_result["corrected_text"] if "corrected_text" in ai_result else target_text
                reason = ai_result["reason"] if "reason" in ai_result else "AI가 제공한 이유 없음"
                context_analysis = ai_result["context_analysis"] if "context_analysis" in ai_result else "AI가 제공한 분석 없음"

                # 로컬 맞춤법 검사 실행
                local_check = self.check_text(corrected)

                final_result: SpellcheckApiResponse = {
                    "success": True,
                    "original_text": target_text,
                    "corrected_text": corrected,
                    "reason": reason,
                    "context_analysis": context_analysis,
                    "errors_found": len(local_check["errors"]),
                    "error_words": local_check["errors"],
                    "accuracy": local_check["stats"]["accuracy"],
                    "total_words": local_check["stats"]["total_words"],
                }
                return final_result

            raise ValueError("AI 응답이 비어있습니다.")

        except json.JSONDecodeError as e:
            logger.error(f"❌ AI 응답 JSON 파싱 오류: {e}")
            return {
                "success": False,
                "error": "AI response is not valid JSON",
                "original_text": target_text,
                "corrected_text": target_text,
                "errors_found": -1,
                "error_words": [],
                "accuracy": 100.0,
                "total_words": len(target_text.split()),
            }
        except Exception as e:
            logger.error(f"❌ AI 기반 문맥 교정 중 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_text": target_text,
                "corrected_text": target_text,
                "errors_found": -1,
                "error_words": [],
                "accuracy": 100.0,
                "total_words": len(target_text.split()),
            }
