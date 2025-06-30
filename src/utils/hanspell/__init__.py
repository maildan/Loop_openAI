# -*- coding: utf-8 -*-
"""
hanspell
~~~~~~~~
Python Korean Spell Checker using Naver Spell Checker
:copyright: (c) 2015 SuHun Han
:license: MIT
"""
from typing import cast, TypedDict
from .response import Checked, HanspellResult
from .constants import CheckResult

import requests
import json
import sys
import time
from collections import OrderedDict
from bs4 import BeautifulSoup

__version__ = "1.1"

_agent = requests.Session()
_base_url = "https://m.search.naver.com/p/csearch/ocontent/spellchecker.nhn"

# API 응답의 정확한 타입 구조 정의
class _ApiResult(TypedDict):
    html: str
    errata_count: int

class _ApiMessage(TypedDict):
    result: _ApiResult

class _ApiResponse(TypedDict):
    message: _ApiMessage


def _remove_tags(text: str) -> str:
    # BeautifulSoup으로 HTML 태그 제거
    return BeautifulSoup(text, "html.parser").get_text()


def check(text: str | list[str]) -> Checked | list[Checked]:
    """
    check(text)
    This function checks korean spelling in the text.
    It returns a Checked object.
    """

    if isinstance(text, list):
        result: list[Checked] = []
        for item in text:
            # 재귀 호출은 항상 Checked 객체를 반환
            checked_item = check(item)
            if isinstance(checked_item, Checked):
                result.append(checked_item)
        return result

    if len(text) > 500:
        return Checked(result=False, original=text, errors=-1)

    payload = {"_callback": "window.__jindo2_callback._spellingCheck_0", "q": text}

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
        "referer": "https://search.naver.com/",
    }

    start_time = time.time()
    try:
        r = _agent.get(_base_url, params=payload, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException:
        return Checked(result=False, original=text)

    passed_time = time.time() - start_time

    json_str = r.text[len(payload["_callback"]) + 1 : -2]

    try:
        # json.loads의 결과를 명시적 TypedDict로 캐스팅
        data = cast(_ApiResponse, json.loads(json_str))
    except (json.JSONDecodeError, KeyError):
        return Checked(result=False, original=text)

    # 캐스팅 후 안전하게 데이터 접근
    html = data["message"]["result"]["html"]
    errata_count = data["message"]["result"]["errata_count"]

    words: OrderedDict[str, int] = OrderedDict()
    soup = BeautifulSoup(html, "html.parser")
    for error in soup.find_all("span", class_="re_red"):
        words[error.text] = CheckResult["WRONG_SPELLING"]
    for error in soup.find_all("span", class_="re_green"):
        words[error.text] = CheckResult["WRONG_SPACING"]
    for error in soup.find_all("span", class_="re_violet"):
        words[error.text] = CheckResult["AMBIGUOUS"]
    for error in soup.find_all("span", class_="re_blue"):
        words[error.text] = CheckResult["STATISTICAL_CORRECTION"]

    result_dict: HanspellResult = {
        "result": True,
        "original": text,
        "checked": _remove_tags(html),
        "errors": errata_count,
        "time": passed_time,
        "words": words,
    }

    return Checked(**result_dict)


spell_checker = sys.modules[__name__]
