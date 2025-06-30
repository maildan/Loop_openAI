#!/usr/bin/env python3
"""
Loop AI 한국어 맞춤법 검사 모듈
- ssut/py-hanspell 라이브러리 (네이버 맞춤법 검사기 기반) 사용
- https://github.com/ssut/py-hanspell
"""

import logging
from typing import cast
from typing_extensions import TypedDict
from .hanspell import spell_checker
from .hanspell.constants import CheckResult
from .hanspell.response import Checked

logger = logging.getLogger(__name__)


class SpellCheckStats(TypedDict):
    total_words: int
    errors: int
    accuracy: float


class FullCheckResult(TypedDict):
    original: str
    corrected: str
    errors: list[str]
    suggestions: dict[str, list[str]]
    stats: SpellCheckStats


class ModuleStats(TypedDict):
    dictionary_size: int
    metadata: dict[str, str]
    status: str


class KoreanSpellChecker:
    """
    py-hanspell 라이브러리를 사용한 한국어 맞춤법 검사기
    """

    def __init__(self):
        """맞춤법 검사기 초기화"""
        logger.info("✅ py-hanspell 맞춤법 검사기 초기화")

    def check_text(self, text: str) -> FullCheckResult:
        """
        텍스트 전체 맞춤법 검사

        Args:
            text: 검사할 텍스트 (최대 500자)

        Returns:
            FullCheckResult: 검사 결과
        """
        if not text:
            return {
                "original": text,
                "corrected": text,
                "errors": [],
                "suggestions": {},
                "stats": {"total_words": 0, "errors": 0, "accuracy": 100.0},
            }

        try:
            # hanspell은 500자 제한이 있음
            if len(text) > 500:
                logger.warning("⚠️ 입력 텍스트가 500자를 초과하여 일부만 검사합니다.")
                text = text[:500]

            result = cast(Checked, spell_checker.check(text))

            error_words = [
                word
                for word, code in result.words.items()
                if code != CheckResult["PASSED"]
            ]

            total_words = len(result.words)
            error_count = result.errors
            accuracy = (
                ((total_words - error_count) / total_words * 100)
                if total_words > 0
                else 100.0
            )

            return {
                "original": result.original,
                "corrected": result.checked,
                "errors": error_words,
                "suggestions": {
                    word: [word] for word in error_words
                },  # py-hanspell은 제안 기능이 없어 단순 표시
                "stats": {
                    "total_words": total_words,
                    "errors": error_count,
                    "accuracy": round(accuracy, 1),
                },
            }
        except Exception as e:
            logger.error(f"❌ 맞춤법 검사 중 오류 발생: {e}")
            return {
                "original": text,
                "corrected": text,
                "errors": [],
                "suggestions": {},
                "stats": {"total_words": 0, "errors": 0, "accuracy": 100.0},
            }

    def is_correct(self, word: str) -> bool:
        """
        단어가 올바른 맞춤법인지 확인.
        py-hanspell은 문장 단위로 검사하므로, 단어 하나도 문장처럼 검사.
        """
        if not word:
            return False

        result = cast(Checked, spell_checker.check(word))
        return result.errors == 0

    def correct_word(self, word: str) -> str:
        """단어 자동 수정"""
        if not word:
            return word

        result = cast(Checked, spell_checker.check(word))
        return result.checked

    def get_suggestions(
        self, word: str, limit: int = 5, _threshold: int = 0
    ) -> list[tuple[str, int]]:
        """
        수정 제안 반환. py-hanspell은 직접적인 제안 리스트를 제공하지 않음.
        대신 수정된 단어를 반환.
        """
        if not word:
            return []

        result = cast(Checked, spell_checker.check(word))
        if result.checked != result.original:
            return [(result.checked, 100)]  # 유사도 100으로 반환
        return []

    def get_stats(self) -> ModuleStats:
        """맞춤법 검사기 통계 정보"""
        return {
            "dictionary_size": -1,  # 외부 API 사용으로 사전 크기 알 수 없음
            "metadata": {"name": "py-hanspell (Naver Spell Checker)"},
            "status": "active",
        }


# 전역 인스턴스
_spellchecker_instance: KoreanSpellChecker | None = None


def get_spellchecker() -> KoreanSpellChecker:
    """싱글톤 맞춤법 검사기 인스턴스 반환"""
    global _spellchecker_instance

    if _spellchecker_instance is None:
        _spellchecker_instance = KoreanSpellChecker()

    return _spellchecker_instance


def check_spelling(text: str) -> FullCheckResult:
    """편의 함수: 텍스트 맞춤법 검사"""
    checker = get_spellchecker()
    return checker.check_text(text)


def suggest_corrections(word: str, limit: int = 5) -> list[tuple[str, int]]:
    """편의 함수: 단어 수정 제안"""
    checker = get_spellchecker()
    return checker.get_suggestions(word, limit=limit)


def correct_word(word: str) -> str:
    """편의 함수: 단어 자동 수정"""
    checker = get_spellchecker()
    return checker.correct_word(word)


def test_spellchecker():
    """맞춤법 검사기 테스트"""
    checker = get_spellchecker()

    test_cases = [
        "아녀하세요",
        "오늘 날씨가 참 조네요.",
        "아버지가방에들어가신다",
        "이거 마춤법 틀린거 마자요?",
        "당신은 멋진 이야기를 만들어낼 수 있는 잠재력을 가지고있습니다.",
    ]

    for text in test_cases:
        print(f"Original: {text}")
        corrected = checker.correct_word(
            text
        )  # 단어 교정이 아닌 문장 교정 함수로 테스트
        print(f"Corrected: {corrected}")

        checked_result = checker.check_text(text)
        print(
            f"Check Result: {json.dumps(checked_result, indent=2, ensure_ascii=False)}"
        )
        print("-" * 20)


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)
    test_spellchecker()
