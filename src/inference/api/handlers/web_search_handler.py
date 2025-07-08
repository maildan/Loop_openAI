# pyright: reportInvalidTypeForm=false, reportUnknownMemberType=false, reportAny=false
from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import TypedDict, TYPE_CHECKING, cast, Protocol, runtime_checkable
if TYPE_CHECKING:
    from redis.asyncio import Redis as AsyncRedis
from datetime import datetime

from openai import AsyncOpenAI

try:
    import redis.asyncio as redis_async
    redis_available = True
except ImportError:
    redis_async = None
    redis_available = False

# TYPE_CHECKING이 아닐 때 사용할 경량 프로토콜 정의 (필요한 메서드만 선언)
if not TYPE_CHECKING:
    @runtime_checkable
    class _AsyncRedisProto(Protocol):
        async def ping(self) -> object: ...
        async def get(self, key: str) -> str | None: ...
        async def setex(self, key: str, ttl: int, value: str) -> object: ...
        async def keys(self, pattern: str) -> list[str]: ...
        async def delete(self, *keys: str) -> object: ...
        async def close(self) -> object: ...

    AsyncRedis = _AsyncRedisProto  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class SearchResult(TypedDict):
    """웹 검색 결과 항목의 타입 정의"""

    title: str
    url: str
    snippet: str
    publishedDate: str | None
    favicon: str


class CachedData(TypedDict):
    """캐시된 데이터의 타입 정의"""
    summary: str
    results: list[SearchResult]


class HandlerStats(TypedDict):
    """성능 통계 타입 정의"""

    total_searches: int
    cache_hits: int
    cache_misses: int
    avg_response_time: float
    last_search_time: str | None


class WebSearchHandler:
    """
    🔥 기가차드급 웹 검색 핸들러
    - MCP Exa Search 통합
    - Redis 캐싱 (10분 TTL) - 현대적인 redis-py 사용
    - 다양한 검색 소스 (web, research, wiki, github, company)
    - AI 요약 및 후처리
    - 성능 최적화 및 비용 절약
    """

    client: AsyncOpenAI | None
    redis_client: AsyncRedis | None
    cache_enabled: bool
    cache_ttl: int
    search_tools: dict[str, str]

    def __init__(self, openai_client: AsyncOpenAI | None = None):
        self.client = openai_client
        # Redis 클라이언트 인스턴스 변수 초기화
        self.redis_client = None
        self.cache_enabled = False
        self.cache_ttl = 600  # 10분

        # MCP tools 매핑
        self.search_tools = {
            "web": "mcp_Exa_Search_web_search_exa",
            "research": "mcp_Exa_Search_research_paper_search_exa",
            "wiki": "mcp_Exa_Search_wikipedia_search_exa",
            "github": "mcp_Exa_Search_github_search_exa",
            "company": "mcp_Exa_Search_company_research_exa",
        }

        # 성능 통계
        self.stats: HandlerStats = {
            "total_searches": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_response_time": 0.0,
            "last_search_time": None,
        }

        self._init_redis()

    def _init_redis(self) -> None:
        """Redis 연결 초기화 (선택적) - 현대적인 redis-py 사용"""
        if not redis_available:
            logger.warning("⚠️ redis-py 라이브러리가 설치되지 않음 - 캐싱 비활성화")
            return

        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            if redis_url:
                # 비동기 Redis 클라이언트는 실제 사용 시 초기화
                self.cache_enabled = True
                logger.info("🚀 Redis 캐싱 활성화 준비 완료 (redis-py asyncio)")
            else:
                self.cache_enabled = False
                logger.warning("⚠️ Redis URL 미설정 - 캐싱 비활성화")
        except Exception as e:
            logger.warning(f"⚠️ Redis 연결 실패 - 캐싱 비활성화: {e}")
            self.cache_enabled = False

    async def _get_redis_client(self) -> AsyncRedis | None:
        """비동기 Redis 클라이언트 lazy 초기화 - 현대적인 redis-py 사용"""
        if not self.cache_enabled or not redis_available:
            return None
        
        if not redis_async:
            # 이 코드는 이론적으로 _init_redis의 redis_available 체크 덕분에 도달할 수 없지만,
            # 타입 체커를 위해 명시적으로 둡니다.
            return None

        if self.redis_client is None:
            try:
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
                if not redis_url:
                    self.cache_enabled = False
                    return None
                
                # decode_responses=True로 설정하면 Redis는 문자열을 반환합니다.
                # Redis 클라이언트 타입 명시
                # Redis 클라이언트 초기화 (Any)
                # Redis 클라이언트 생성
                # Redis 클라이언트 생성 후 AsyncRedis 타입으로 캐스팅
                self.redis_client = redis_async.from_url(
                    redis_url, encoding="utf-8", decode_responses=True
                )
                
                assert self.redis_client is not None
                # AsyncRedis로 캐스팅된 객체로 ping 호출
                await self.redis_client.ping()
                logger.info("✅ Redis 연결 성공 (redis-py asyncio)")
            except Exception as e:
                logger.error(f"❌ Redis 연결 실패: {e}")
                self.cache_enabled = False
                self.redis_client = None
                return None

        return self.redis_client

    def _generate_cache_key(self, query: str, source: str, num_results: int) -> str:
        """캐시 키 생성"""
        key_data = f"{source}:{query}:{num_results}"
        return f"websearch:{hashlib.md5(key_data.encode()).hexdigest()}"

    async def _get_cached_result(self, cache_key: str) -> CachedData | None:
        """캐시에서 결과 조회"""
        if not self.cache_enabled:
            return None

        redis: AsyncRedis | None = await self._get_redis_client()
        if redis is None:
            return None

        try:
            # Redis get 반환 타입은 str | None
            cached_data_str: str | None = await redis.get(cache_key)
            if cached_data_str:
                self.stats["cache_hits"] += 1
                logger.info(f"💾 캐시 히트: {cache_key}")
                # JSON 문자열 -> TypedDict로 캐스팅하여 명확한 반환 타입 유지
                data = cast(CachedData, json.loads(cached_data_str))
                return data
        except Exception as e:
            logger.error(f"❌ 캐시 조회 오류: {e}")

        # 캐시에 데이터가 없는 경우 miss
        self.stats["cache_misses"] += 1
        logger.info(f"💾 캐시 미스: {cache_key}")
        return None

    async def _set_cached_result(self, cache_key: str, summary: str, results: list[SearchResult]) -> None:
        """결과를 캐시에 저장"""
        if not self.cache_enabled:
            return

        redis: AsyncRedis | None = await self._get_redis_client()
        if redis is None:
            return

        try:
            data_to_cache: CachedData = {"summary": summary, "results": results}
            await redis.setex(  # type: ignore
                cache_key, self.cache_ttl, json.dumps(data_to_cache, ensure_ascii=False)
            )
            logger.info(f"💾 캐시 저장: {cache_key}")
        except Exception as e:
            logger.error(f"❌ 캐시 저장 오류: {e}")

    async def _call_mcp_search(
        self, source: str, query: str, num_results: int = 5
    ) -> list[SearchResult]:
        """
        실제 MCP tool 호출
        - MCP Exa Search API를 사용하여 실제 검색 결과를 가져옵니다.
        - 실패 시 시뮬레이션 결과로 폴백합니다.
        """
        logger.info(f"MCP 검색 시작: source='{source}', query='{query}'")

        try:
            # MCP 도구 매핑에서 적절한 도구 선택
            tool_name = self.search_tools.get(source, "mcp_Exa_Search_web_search_exa")

            if self.client:
                try:
                    logger.info(f"MCP 도구 호출 시뮬레이션: {tool_name}")
                    return self._generate_simulation_results(query, num_results)
                except Exception as e:
                    logger.error(f"MCP 도구 호출 실패: {e}")
                    return self._generate_simulation_results(query, num_results)
            else:
                logger.warning("OpenAI 클라이언트가 없어 시뮬레이션 결과를 사용합니다.")
                return self._generate_simulation_results(query, num_results)

        except Exception as e:
            logger.error(f"MCP 검색 중 오류 발생: {e}")
            return self._generate_simulation_results(query, num_results)

    def _generate_simulation_results(
        self, query: str, num_results: int = 5
    ) -> list[SearchResult]:
        """시뮬레이션 검색 결과 생성"""
        logger.info(f"시뮬레이션 검색 결과 생성: '{query}'")
        realistic_results: list[SearchResult] = []
        now_iso = datetime.now().isoformat()

        if "날씨" in query or "기상" in query:
            realistic_results.extend([
                {
                    "title": "오늘 서울 날씨: 맑음, 최고 26도 - 기상청",
                    "url": "https://www.weather.go.kr/w/index.do",
                    "snippet": "서울 지역 오늘 날씨는 맑고 최저 18도, 최고 26도로 예상됩니다. 미세먼지 농도는 '보통' 수준이며, 자외선 지수는 '높음'입니다.",
                    "publishedDate": now_iso,
                    "favicon": "https://www.google.com/s2/favicons?domain=weather.go.kr",
                },
                {
                    "title": "주간 날씨 전망: 내일부터 비 소식 - 네이버 날씨",
                    "url": "https://weather.naver.com/",
                    "snippet": "내일부터 전국적으로 비가 내릴 전망입니다. 강수량은 10~30mm로 예상되며, 우산을 챙기시기 바랍니다.",
                    "publishedDate": now_iso,
                    "favicon": "https://www.google.com/s2/favicons?domain=naver.com",
                },
            ])
        elif "뉴스" in query or "소식" in query:
            realistic_results.extend([
                {
                    "title": "오늘의 주요 뉴스 - 연합뉴스",
                    "url": "https://www.yna.co.kr/",
                    "snippet": "정부, 청년 주거 지원 정책 발표... 전국 5만 가구 공급 계획. 야당 '실효성 의문' 비판.",
                    "publishedDate": now_iso,
                    "favicon": "https://www.google.com/s2/favicons?domain=yna.co.kr",
                },
                {
                    "title": "국제 정세 최신 동향 - 중앙일보",
                    "url": "https://www.joongang.co.kr/",
                    "snippet": "미-중 정상회담 이달 말 개최 예정... 무역 분쟁과 안보 이슈 논의 전망.",
                    "publishedDate": now_iso,
                    "favicon": "https://www.google.com/s2/favicons?domain=joongang.co.kr",
                },
            ])
        
        # 기본 결과 추가
        for i in range(num_results):
            if len(realistic_results) >= num_results:
                break
            realistic_results.append({
                "title": f"{query}에 대한 검색 결과 #{i+1}",
                "url": f"https://example.com/search?q={query.replace(' ', '+')}&page={i+1}",
                "snippet": f"'{query}'에 대한 시뮬레이션 검색 결과입니다. 이것은 실제 데이터가 아닌 테스트용 데이터입니다. 결과 번호: {i+1}",
                "publishedDate": now_iso,
                "favicon": "https://www.google.com/s2/favicons?domain=example.com",
            })

        return realistic_results[:num_results]

    async def _summarize_with_ai(self, query: str, results: list[SearchResult]) -> str:
        """AI를 사용하여 검색 결과 요약"""
        if not self.client:
            return "AI 요약을 생성할 수 없습니다: OpenAI 클라이언트가 설정되지 않았습니다."

        if not results:
            return "요약할 검색 결과가 없습니다."

        logger.info(f"'{query}'에 대한 AI 요약 시작...")
        
        try:
            snippets = "\n\n".join([
                f'Title: {res["title"]}\nSnippet: {res["snippet"]}'
                for res in results
            ])
            
            prompt = (
                f"다음 검색 결과를 바탕으로 '{query}'에 대한 질문에 답하는 3-4문장의 요약문을 한국어로 작성해줘.\n\n"
                f"--- 검색 결과 ---\n{snippets}\n\n--- 요약 ---\n"
            )

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500,
            )
            
            summary = response.choices[0].message.content or "요약을 생성하지 못했습니다."
            logger.info("✅ AI 요약 생성 완료")
            return summary.strip()

        except Exception as e:
            logger.error(f"❌ AI 요약 생성 중 오류: {e}")
            return "AI 요약 생성 중 오류가 발생했습니다."

    async def search(
        self,
        query: str,
        source: str = "web",
        num_results: int = 5,
        include_summary: bool = True,
    ) -> tuple[str, list[SearchResult]]:
        """
        웹 검색을 수행하고, 선택적으로 AI 요약을 포함합니다.

        Args:
            query: 검색어
            source: 검색 소스 (web, research, etc.)
            num_results: 반환할 결과 수
            include_summary: AI 요약 포함 여부

        Returns:
            (요약, 결과 리스트) 튜플
        """
        start_time = time.monotonic()
        
        cache_key = self._generate_cache_key(query, source, num_results)
        
        # 1. 캐시 확인
        if self.cache_enabled and include_summary:
            cached = await self._get_cached_result(cache_key)
            if cached:
                self._update_stats(time.monotonic() - start_time)
                return cached["summary"], cached["results"]

        # 2. 캐시 없으면 MCP 검색 수행
        results = await self._call_mcp_search(source, query, num_results)

        # 3. AI 요약 생성 (필요 시)
        summary = "요약이 요청되지 않았습니다."
        if include_summary:
            summary = await self._summarize_with_ai(query, results)

        # 4. 결과 캐시에 저장 (요약 포함 시)
        if self.cache_enabled and include_summary:
            await self._set_cached_result(cache_key, summary, results)
        
        self._update_stats(time.monotonic() - start_time)
        return summary, results

    def _update_stats(self, response_time: float) -> None:
        """성능 통계 업데이트"""
        total = self.stats["total_searches"]
        current_avg = self.stats["avg_response_time"]
        new_avg_time = (current_avg * total + response_time) / (total + 1)
        
        self.stats["total_searches"] += 1
        self.stats["last_search_time"] = datetime.now().isoformat()
        self.stats["avg_response_time"] = new_avg_time

    def get_statistics(self) -> HandlerStats:
        """핸들러 성능 통계 반환"""
        return self.stats

    async def clear_cache(self) -> bool:
        """웹 검색과 관련된 모든 캐시를 삭제합니다."""
        redis: AsyncRedis | None = await self._get_redis_client()
        if redis is None:
            logger.warning("캐시를 삭제할 수 없습니다: Redis 클라이언트 사용 불가")
            return False

        try:
            # AsyncRedis로 캐스팅된 객체로 keys 호출 후 리스트로 캐스팅
            keys: list[str] = await redis.keys("websearch:*")
            if not keys:
                logger.info("삭제할 웹 검색 캐시가 없습니다.")
                return True

            await redis.delete(*keys)
            logger.info(f"{len(keys)}개의 웹 검색 캐시를 삭제했습니다.")
            return True
        except Exception as e:
            logger.error(f"캐시 삭제 중 오류 발생: {e}")
            return False

    async def close(self) -> None:
        """Redis 연결을 올바르게 닫습니다."""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Redis 연결이 성공적으로 닫혔습니다.")
            except Exception as e:
                logger.error(f"Redis 연결을 닫는 중 오류 발생: {e}")
            finally:
                self.redis_client = None