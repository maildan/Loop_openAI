"""
Loop AI 맞춤법 검사 핸들러
서버의 맞춤법 검사 관련 로직을 모듈화
"""

import logging
from typing import TypedDict, Any
import sys
import os

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


class SpellCheckHandler:
    """맞춤법 검사 핸들러"""

    spellchecker: KoreanSpellChecker

    def __init__(self):
        """맞춤법 검사 핸들러 초기화"""
        self.spellchecker = get_spellchecker()
        logger.info("✅ 맞춤법 검사 핸들러 초기화 완료")

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
                "corrected_text": check_result["corrected"] if auto_correct else text,
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
