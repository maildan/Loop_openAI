#!/usr/bin/env python3
"""
Loop AI 모듈화된 추론 서버
맞춤법 검사 기능과 채팅 기능을 통합한 창작 지원 시스템
"""

import logging
import os
import sys
import time
from collections import OrderedDict
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Generic, TypeVar, TypedDict, Any, TYPE_CHECKING

import uvicorn
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI, APIConnectionError
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

# MCP 관련 임포트 추가
mcp_available = False
try:
    # MCP 라이브러리 임포트 시도
    from mcp.server.fastmcp import FastMCP

    mcp_available = True
    logger = logging.getLogger(__name__)
    logger.info("✅ MCP 라이브러리 임포트 성공")
except ImportError:
    FastMCP = None
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ MCP 라이브러리 임포트 실패: MCP 비활성화")

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

# 로컬 모듈 import
from src.inference.api.handlers import ChatHandler, SpellCheckHandler
from src.inference.api.handlers.google_docs_handler import GoogleDocsHandler
from src.inference.api.handlers.location_handler import LocationHandler
from src.inference.api.handlers.web_search_handler import WebSearchHandler
from src.utils.spellcheck import ModuleStats
from src.shared.prompts import loader as prompt_loader


# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# --- TypedDict 정의 ---
class ChatCompletionResult(TypedDict):
    response: str
    model: str
    cost: float
    tokens: int
    isComplete: bool | None
    continuationToken: str | None


class SpellCheckResult(TypedDict):
    success: bool
    original_text: str
    corrected_text: str
    errors_found: int
    error_words: list[str]
    accuracy: float
    total_words: int


class WebSearchResultDict(TypedDict):
    title: str
    url: str
    snippet: str
    publishedDate: str | None
    favicon: str | None


class WebSearchAPIResult(TypedDict):
    query: str
    source: str
    num_results: int
    results: list[WebSearchResultDict]
    summary: str
    timestamp: str
    from_cache: bool
    response_time: float


class WebSearchStatsResult(TypedDict):
    total_searches: int
    cache_hits: int
    cache_misses: int
    avg_response_time: float
    last_search_time: str | None
    cache_enabled: bool


# 전역 변수
openai_client: AsyncOpenAI | None = None
chat_handler: ChatHandler | None = None
spellcheck_handler: SpellCheckHandler | None = None
location_handler: LocationHandler | None = None
web_search_handler: WebSearchHandler | None = None
google_docs_handler: GoogleDocsHandler | None = None
mcp_server: Any = None


@asynccontextmanager
async def lifespan(_app: "FastAPI") -> AsyncGenerator[None, None]:
    """서버 시작 및 종료 시 실행되는 이벤트 핸들러"""
    global openai_client, chat_handler, spellcheck_handler, location_handler, web_search_handler, google_docs_handler, mcp_server
    logger.info("🚀 서버 시작 이벤트 발생")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않아 외부 API 연동 기능이 제한됩니다.")

    # 더 견고한 HTTP 클라이언트를 위한 타임아웃 설정
    timeout = httpx.Timeout(10.0, connect=5.0)
    openai_client = AsyncOpenAI(api_key=api_key, timeout=timeout)
    logger.info("✅ (Async) OpenAI 클라이언트 초기화 완료 (타임아웃 설정 적용)")

    # 핸들러 초기화
    chat_handler = ChatHandler(openai_client)
    spellcheck_handler = SpellCheckHandler(openai_client)
    location_handler = LocationHandler()
    web_search_handler = WebSearchHandler(openai_client)
    google_docs_handler = GoogleDocsHandler()

    chat_handler.load_datasets()
    logger.info("✅ 모든 핸들러 및 데이터셋 초기화 완료")

    # MCP 서버 설정
    if mcp_available and FastMCP is not None:
        try:
            mcp_server = FastMCP("loop_ai", stateless_http=True)
            logger.info("✅ MCP 서버 초기화 완료")
        except Exception as e:
            logger.error(f"❌ MCP 서버 초기화 실패: {e}")
            mcp_server = None
    yield
    logger.info("🌙 서버 종료.")


# FastAPI 앱 생성
app = FastAPI(
    title="Loop AI API",
    description="Loop AI 창작 지원 시스템 - 채팅, 맞춤법 검사, 시놉시스 생성",
    version="3.0.0",
    lifespan=lifespan,
)


# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip 압축 미들웨어 추가: 모든 응답을 압축하여 네트워크 전송량을 최소화합니다.
# minimum_size=1000: 1000바이트 이상의 응답만 압축합니다.
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 비용 추적
PRICING_PER_TOKEN = {
    "gpt-4o-mini": {"input": 0.00015 / 1000, "output": 0.0006 / 1000},
    "gpt-4o": {"input": 0.005 / 1000, "output": 0.015 / 1000},
    "gpt-3.5-turbo": {"input": 0.0005 / 1000, "output": 0.0015 / 1000},
}

monthly_usage = {"cost": 0.0, "tokens": 0}
MONTHLY_BUDGET = float(os.getenv("OPENAI_MONTHLY_BUDGET", "15.0"))

# LRU 캐시 제네릭 타입 정의
K = TypeVar("K")
V = TypeVar("V")


# LRU 캐시 구현
class LRUCache(Generic[K, V]):
    def __init__(self, capacity: int = 1024):
        self.cache: OrderedDict[K, V] = OrderedDict()
        self.capacity: int = capacity

    def get(self, key: K) -> V | None:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: K, value: V) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.capacity:
            _ = self.cache.popitem(last=False)
        self.cache[key] = value


response_cache: LRUCache[str, str] = LRUCache()


# API 모델 정의
class ChatMessage(BaseModel):
    role: str = Field(..., description="메시지 역할 (user/assistant)")
    content: str = Field(..., description="메시지 내용")


class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 메시지")
    history: list[ChatMessage] = Field(default=[], description="채팅 히스토리")
    model: str | None = Field(None, description="사용할 모델")
    maxTokens: int = Field(4000, description="최대 토큰 수")
    isLongForm: bool = Field(False, description="긴 텍스트 생성 모드")
    continueStory: bool = Field(False, description="이야기 계속하기 모드")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI 응답")
    model: str = Field(..., description="사용된 모델")
    cost: float = Field(..., description="비용 (USD)")
    tokens: int = Field(..., description="사용된 토큰 수")
    isComplete: bool | None = Field(True, description="응답 완료 여부")


class SpellCheckRequest(BaseModel):
    text: str = Field(..., description="맞춤법 검사할 텍스트")
    auto_correct: bool = Field(default=True, description="자동 수정 여부")
    # AI 기반 교정을 위한 필드 추가
    full_document: str | None = Field(None, description="전체 문서 컨텍스트")
    use_ai: bool = Field(default=False, description="AI 기반 문맥 교정 사용 여부")


class SpellCheckResponse(BaseModel):
    original_text: str = Field(..., description="원본 텍스트")
    corrected_text: str = Field(..., description="수정된 텍스트")
    errors_found: int = Field(..., description="발견된 오타 수")
    error_words: list[str] = Field(..., description="오타 단어 목록")
    accuracy: float = Field(..., description="정확도 (%)")
    total_words: int = Field(..., description="총 단어 수")
    # AI 기반 교정 결과를 위한 필드 추가
    reason: str | None = Field(None, description="AI 교정 이유")
    context_analysis: str | None = Field(None, description="AI 문맥 분석 결과")


class CostStatusResponse(BaseModel):
    monthly_cost: float
    monthly_budget: float
    usage_percentage: float
    total_tokens: int
    cache_hits: int


class LocationSuggestRequest(BaseModel):
    query: str = Field(..., description="추천을 위한 검색어 (도시/지역명)")


class LocationSuggestResponse(BaseModel):
    suggestions: list[str] = Field(..., description="추천된 지역·도시명 목록")


class WebSearchRequest(BaseModel):
    query: str = Field(..., description="검색어")
    source: str = Field(
        default="web", description="검색 소스 (web, research, wiki, github, company)"
    )
    num_results: int = Field(default=5, ge=1, le=10, description="결과 개수 (1-10)")
    include_summary: bool = Field(default=True, description="AI 요약 포함 여부")


class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    publishedDate: str | None = None
    favicon: str | None = None


class WebSearchResponse(BaseModel):
    query: str
    source: str
    num_results: int
    results: list[WebSearchResult]
    summary: str = ""
    timestamp: str
    from_cache: bool = False
    response_time: float


class WebSearchStatsResponse(BaseModel):
    total_searches: int
    cache_hits: int
    cache_misses: int
    avg_response_time: float
    last_search_time: str | None
    cache_enabled: bool


def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    """토큰 사용량에 따른 비용 계산"""
    model_pricing = PRICING_PER_TOKEN.get(model, {"input": 0, "output": 0})
    cost = (
        prompt_tokens * model_pricing["input"]
        + completion_tokens * model_pricing["output"]
    )
    monthly_usage["cost"] += cost
    monthly_usage["tokens"] += prompt_tokens + completion_tokens
    return cost


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Loop AI 서버가 실행 중입니다."}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> StreamingResponse:
    """
    채팅 엔드포인트. 스트리밍 응답을 사용하여 실시간 타이핑 효과를 제공합니다.
    """
    if not chat_handler or not openai_client:
        raise HTTPException(
            status_code=503,
            detail="서버가 아직 준비되지 않았습니다. 잠시 후 다시 시도해주세요.",
        )

    try:
        # 1. 사용자 의도 및 레벨 파악
        intent, level = chat_handler.detect_intent_and_level(request.message)

        # 2. 의도에 따른 동적 프롬프트 생성 또는 핸들러 호출
        if intent == "web_search":
            generator = chat_handler.handle_web_search(request.message)
        else:
            # 2a. 프롬프트 생성 (intent가 프롬프트 템플릿 이름과 일치한다고 가정)
            prompt = prompt_loader.get_prompt(
                intent, user_message=request.message, level=level
            )
            # 2b. 프롬프트를 사용하여 스트리밍 응답 생성
            generator = chat_handler.generate_response(
                prompt=prompt,
                max_tokens=request.maxTokens,
                temperature=0.7,
            )
        
        # 3. 스트리밍 응답 반환
        return StreamingResponse(generator, media_type="text/event-stream")

    except ValueError as e:
        logger.error(f"프롬프트 생성 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except APIConnectionError as e:
        logger.error(f"OpenAI API 연결 오류: {e.__cause__}")
        raise HTTPException(
            status_code=503, detail="외부 API 서비스에 연결할 수 없습니다."
        )
    except Exception as e:
        logger.exception(f"채팅 처리 중 예상치 못한 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="내부 서버 오류가 발생했습니다.")


@app.post("/api/spellcheck", response_model=SpellCheckResponse)
async def spellcheck_endpoint(request: SpellCheckRequest) -> SpellCheckResponse:
    """맞춤법 검사 엔드포인트"""
    if not spellcheck_handler:
        raise HTTPException(
            status_code=503,
            detail="서버가 아직 준비되지 않았습니다. 잠시 후 다시 시도해주세요.",
        )

    try:
        if request.use_ai and request.full_document:
            # AI 기반 문맥 교정
            result = await spellcheck_handler.context_aware_correction(
                target_text=request.text, full_document=request.full_document
            )
        else:
            # 기존 로컬 교정
            result = spellcheck_handler.create_spellcheck_response(
                request.text, request.auto_correct
            )
        
        # TypedDict에서 Pydantic 모델로 안전하게 변환
        return SpellCheckResponse(
            original_text=result.get("original_text", request.text),
            corrected_text=result.get("corrected_text", request.text),
            errors_found=result.get("errors_found", 0),
            error_words=result.get("error_words", []),
            accuracy=result.get("accuracy", 100.0),
            total_words=result.get("total_words", 0),
            reason=result.get("reason"),
            context_analysis=result.get("context_analysis"),
        )

    except Exception as e:
        logger.exception(f"맞춤법 검사 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cost-status", response_model=CostStatusResponse)
async def get_cost_status():
    """월별 비용 사용 현황 조회"""
    cost = monthly_usage["cost"]
    tokens = monthly_usage["tokens"]
    usage_percentage = (cost / MONTHLY_BUDGET) * 100 if MONTHLY_BUDGET > 0 else 0

    return CostStatusResponse(
        monthly_cost=round(cost, 4),
        monthly_budget=MONTHLY_BUDGET,
        usage_percentage=round(usage_percentage, 2),
        total_tokens=int(tokens),
        cache_hits=response_cache.capacity - len(response_cache.cache),
    )


@app.get("/api/spellcheck/stats")
async def get_spellcheck_stats() -> ModuleStats:
    """맞춤법 검사기 통계 조회"""
    if not spellcheck_handler:
        raise HTTPException(status_code=503, detail="맞춤법 검사기 준비 안됨")
    return spellcheck_handler.get_statistics()


@app.get("/api/health")
async def health_check():
    """
    서버의 상태를 확인하는 헬스 체크 엔드포인트입니다.
    - OpenAI API 연결 상태 확인
    - 핸들러 초기화 여부 확인
    """
    status = {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
    details = {}

    # OpenAI 연결 상태 확인
    if openai_client:
        try:
            _ = await openai_client.models.list(timeout=5)
            details["openai_api"] = "connected"
        except Exception as e:
            details["openai_api"] = f"disconnected: {e}"
            status["status"] = "error"
    else:
        details["openai_api"] = "not_initialized"
        status["status"] = "error"

    # 핸들러 초기화 확인
    details["chat_handler"] = "initialized" if chat_handler else "not_initialized"
    if not chat_handler:
        status["status"] = "error"
        
    if status["status"] == "ok":
        return status
    else:
        raise HTTPException(status_code=503, detail=details)


@app.post("/api/location-suggest", response_model=LocationSuggestResponse)
async def suggest_locations(request: LocationSuggestRequest) -> LocationSuggestResponse:
    """지역/도시명 추천 엔드포인트"""
    if not location_handler:
        raise HTTPException(status_code=503, detail="Location handler not ready")

    suggestions = location_handler.suggest_locations(request.query)
    return LocationSuggestResponse(suggestions=suggestions)


@app.post("/api/web-search", response_model=WebSearchResponse)
async def web_search(request: WebSearchRequest) -> WebSearchResponse:
    """웹 검색 엔드포인트"""
    if not web_search_handler:
        raise HTTPException(status_code=503, detail="Web search handler not ready")

    start_time = time.time()
    # search 메서드는 (summary, results_list) 튜플을 반환
    summary, search_results = await web_search_handler.search(
        query=request.query,
        source=request.source,
        num_results=request.num_results,
        include_summary=request.include_summary,
    )
    end_time = time.time()

    # WebSearchResult 모델로 변환
    validated_results = [WebSearchResult(**r) for r in search_results]

    return WebSearchResponse(
        query=request.query, # 요청에서 query를 가져옴
        source=request.source, # 요청에서 source를 가져옴
        num_results=len(validated_results),
        results=validated_results,
        summary=summary,
        timestamp=datetime.fromtimestamp(start_time).isoformat(),
        from_cache=False, # TODO: 캐시 로직과 연동 필요
        response_time=(end_time - start_time),
    )


@app.get("/api/web-search/stats", response_model=WebSearchStatsResponse)
async def get_web_search_stats() -> WebSearchStatsResponse:
    """웹 검색 통계 조회"""
    if not web_search_handler:
        raise HTTPException(status_code=503, detail="Web search handler not ready")
    stats = web_search_handler.get_statistics()
    # TypedDict를 Pydantic 모델로 안전하게 변환
    return WebSearchStatsResponse(
        total_searches=stats.get("total_searches", 0),
        cache_hits=stats.get("cache_hits", 0),
        cache_misses=stats.get("cache_misses", 0),
        avg_response_time=stats.get("avg_response_time", 0.0),
        last_search_time=stats.get("last_search_time"),
        cache_enabled=stats.get("cache_enabled", False),
    )


@app.delete("/api/web-search/cache")
async def clear_web_search_cache():
    """웹 검색 캐시 삭제"""
    if not web_search_handler:
        raise HTTPException(status_code=503, detail="Web search handler not ready")
    _ = await web_search_handler.clear_cache()
    return {"message": "Web search cache cleared successfully."}


@app.post("/api/clear_cache")
async def clear_cache_endpoint():
    """
    서버의 모든 캐시를 삭제합니다.
    """
    if chat_handler:
        _ = chat_handler.clear_cache()
    if web_search_handler:
        _ = await web_search_handler.clear_cache()
    response_cache.cache.clear()
    logger.info("모든 서버 캐시가 성공적으로 삭제되었습니다.")
    return {"message": "All server caches cleared successfully."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
