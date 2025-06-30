import os
import logging
from typing import List

import requests

logger = logging.getLogger(__name__)


class LocationHandler:
    """Neutrino API를 이용한 지역·도시명 추천 핸들러"""

    BASE_URL = "https://neutrinoapi.net/geocode-address"

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

    def suggest_locations(self, query: str, limit: int = 5) -> List[str]:
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

            response = requests.post(self.BASE_URL, data=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            locations = data.get("locations", [])
            results = []
            for loc in locations:
                # 도시, 국가, 주소 등을 조합하여 가독성 있는 문자열 생성
                parts = []
                for key in ["city", "state", "country", "address"]:
                    value = loc.get(key)
                    if value and value not in parts:
                        parts.append(value)
                label = ", ".join(parts)
                if label and label not in results:
                    results.append(label)
                if len(results) >= limit:
                    break

            logger.info(f"📍 Neutrino 위치 추천 결과 {len(results)}개 반환")
            return results

        except Exception as e:
            logger.error(f"❌ Neutrino 위치 추천 오류: {e}")
            return []
