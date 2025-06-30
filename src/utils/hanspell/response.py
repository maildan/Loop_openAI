# -*- coding: utf-8 -*-
from collections import OrderedDict
from typing import TypedDict, MutableMapping
from .constants import CheckResult

__all__ = ["Checked", "CheckResult", "HanspellResult"]


class HanspellResult(TypedDict):
    """Hanspell API 응답의 JSON 구조"""

    result: bool
    original: str
    checked: str
    errors: int
    time: float
    words: "OrderedDict[str, int]"


class Checked:
    """맞춤법 검사 결과"""

    result: bool
    original: str
    checked: str
    errors: int
    time: float
    words: MutableMapping[str, int]

    def __init__(
        self,
        result: bool = False,
        original: str = "",
        checked: str = "",
        errors: int = 0,
        time: float = 0.0,
        words: MutableMapping[str, int] | None = None,
    ):
        self.result = result
        self.original = original
        self.checked = checked
        self.errors = errors
        self.time = time
        self.words = words if words is not None else OrderedDict()

    def __str__(self) -> str:
        return self.checked

    def __repr__(self) -> str:
        return (
            f"Checked(result={self.result}, original='{self.original}',"
            f" checked='{self.checked}', errors={self.errors}, words={self.words})"
        )

    def as_dict(self) -> HanspellResult:
        # 'words'의 타입이 호환되도록 보장
        words_ordered_dict = (
            self.words
            if isinstance(self.words, OrderedDict)
            else OrderedDict(self.words)
        )
        return {
            "result": self.result,
            "original": self.original,
            "checked": self.checked,
            "errors": self.errors,
            "time": self.time,
            "words": words_ordered_dict,
        }
