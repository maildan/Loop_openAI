import os
import logging
from typing import cast, TypedDict  # safe type casting 및 TypedDict 정의

import httpx  # async HTTP client

logger = logging.getLogger(__name__)

# TypedDict definitions for Neutrino API
class NeutrinoLocation(TypedDict, total=False):
    city: str
    state: str
    country: str
    address: str

class NeutrinoResponse(TypedDict):
    locations: list[NeutrinoLocation]


class LocationHandler:
    """Neutrino API를 이용한 지역·도시명 추천 핸들러"""
    BASE_URL: str = "https://neutrinoapi.net/geocode-address"
    user_id: str | None  # from environment
    api_key: str | None   # from environment
    enabled: bool         # handler 활성화 여부

    def __init__(self):
        # 환경변수에서 자격증명 읽기
        self.user_id = os.getenv("KEY_TAG") or os.getenv("NEUTRINO_USER_ID")
        self.api_key = os.getenv("KEY") or os.getenv("NEUTRINO_API_KEY")

        if not self.user_id or not self.api_key:
            logger.warning(
                "⚠️ Neutrino API 자격증명이 설정되지 않았습니다. LocationHandler 비활성화!"
            )
            self.enabled = False
        else:
            self.enabled = True
            logger.info("🌐 Neutrino LocationHandler 초기화 완료!")

    async def suggest_locations(self, query: str, limit: int = 5) -> list[str]:
        """사용자 쿼리에 대해 지역/도시명을 추천

        Args:
            query: 사용자가 입력한 검색어 (부분 주소, 도시명 등)
            limit: 반환할 최대 추천 수
        Returns:
            지역·도시명 문자열 리스트 (중복 제거)
        """
        if not self.enabled:
            return []

        try:
            payload = {
                "user-id": self.user_id,
                "api-key": self.api_key,
                "address": query,
                "language-code": "ko",
                "fuzzy-search": "true",
            }

            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
                response = await client.post(self.BASE_URL, data=payload)
            # 상태 코드 확인 후 예외 발생 여부 체크
            _ = response.raise_for_status()
            # API 응답을 dict[str, object]로 캐스팅하여 Any 제거
            raw = cast(dict[str, object], response.json())
            # TypedDict으로 캐스팅: dict -> object -> TypedDict (Pyright 호환)
            data = cast(NeutrinoResponse, cast(object, raw))

            locs = data.get("locations", [])
            # NeutrinoLocation 형식으로 캐스팅
            locations_list: list[NeutrinoLocation] = [item for item in locs]
            results: list[str] = []
            for loc in locations_list:
                # 도시, 국가, 주소 등을 조합하여 가독성 있는 문자열 생성
                parts: list[str] = []
                for key in ["city", "state", "country", "address"]:
                    val = loc.get(key)
                    if isinstance(val, str) and val not in parts:
                        parts.append(val)
                label = ", ".join(parts)
                if label and label not in results:
                    results.append(label)
                if len(results) >= limit:
                    break

            logger.info(f"📍 Neutrino 위치 추천 결과 {len(results)}개 반환")
            return results

        except Exception as e:
            logger.error(f"❌ Neutrino 위치 추천 오류: {e}")
            raise
