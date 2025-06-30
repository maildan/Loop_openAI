#!/usr/bin/env python3
"""
Loop AI 모듈화된 추론 서버
맞춤법 검사 기능과 채팅 기능을 통합한 창작 지원 시스템
"""

import logging
import os
import sys
from collections import OrderedDict
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Generic, TypeVar, cast, TypedDict, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

# MCP 관련 임포트 추가
mcp_available = False
try:
    # MCP 라이브러리 임포트 시도
    from mcp.server.fastmcp import FastMCP

    mcp_available = True
    logger = logging.getLogger(__name__)
    logger.info("✅ MCP 라이브러리 임포트 성공")
except ImportError:
    FastMCP = None  # type: ignore
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ MCP 라이브러리 임포트 실패: MCP 비활성화")

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

# 로컬 모듈 import
try:
    from src.inference.api.handlers import ChatHandler, SpellCheckHandler
    from src.inference.api.handlers.chat_handler import ChatHistoryItem
    from src.inference.api.handlers.google_docs_handler import GoogleDocsHandler
    from src.inference.api.handlers.location_handler import LocationHandler
    from src.inference.api.handlers.web_search_handler import (
        SearchResult,
        WebSearchHandler,
    )
    from src.utils.spellcheck import ModuleStats
except ImportError:
    # 상대 import 실패 시 절대 import 시도
    sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))
    from src.inference.api.handlers import ChatHandler, SpellCheckHandler
    from src.inference.api.handlers.chat_handler import ChatHistoryItem
    from src.inference.api.handlers.google_docs_handler import GoogleDocsHandler
    from src.inference.api.handlers.location_handler import LocationHandler
    from src.inference.api.handlers.web_search_handler import (
        SearchResult,
        WebSearchHandler,
    )
    from src.utils.spellcheck import ModuleStats

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
async def lifespan(_app: "FastAPI"):
    """서버 시작 및 종료 시 실행되는 이벤트 핸들러"""
    global openai_client, chat_handler, spellcheck_handler, location_handler, web_search_handler, google_docs_handler, mcp_server
    logger.info("🚀 서버 시작 이벤트 발생")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않아 외부 API 연동 기능이 제한됩니다.")

    openai_client = AsyncOpenAI(api_key=api_key)
    logger.info("✅ (Async) OpenAI 클라이언트 초기화 완료")

    # 핸들러 초기화
    chat_handler = ChatHandler(openai_client)
    spellcheck_handler = SpellCheckHandler()
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
    allow_origins=["http://localhost:4000"],  # 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    continuationToken: str | None = Field(None, description="계속하기 토큰")


class SpellCheckRequest(BaseModel):
    text: str = Field(..., description="맞춤법 검사할 텍스트")
    auto_correct: bool = Field(default=True, description="자동 수정 여부")


class SpellCheckResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    original_text: str = Field(..., description="원본 텍스트")
    corrected_text: str = Field(..., description="수정된 텍스트")
    errors_found: int = Field(..., description="발견된 오타 수")
    error_words: list[str] = Field(..., description="오타 단어 목록")
    accuracy: float = Field(..., description="정확도 (%)")
    total_words: int = Field(..., description="총 단어 수")


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
    pricing = PRICING_PER_TOKEN.get(model, {"input": 0, "output": 0})
    cost = (
        prompt_tokens * pricing["input"] + completion_tokens * pricing["output"]
    )
    monthly_usage["cost"] += cost
    monthly_usage["tokens"] += prompt_tokens + completion_tokens
    return cost


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Loop AI API Server is running."}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """채팅 메시지를 처리하고 AI의 응답을 반환합니다."""
    if not chat_handler:
        raise HTTPException(status_code=503, detail="채팅 핸들러가 초기화되지 않았습니다.")

    try:
        # Pydantic 모델을 TypedDict로 변환
        history_dicts: list[ChatHistoryItem] = [
            {"role": msg.role, "content": msg.content} for msg in request.history
        ]
        result = await chat_handler.handle_request(
            user_message=request.message, _history=history_dicts
        )
        return ChatResponse.model_validate(result)
    except Exception as e:
        logger.error(f"❌ 채팅 처리 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="채팅 처리 중 오류가 발생했습니다.")


@app.post("/api/spellcheck", response_model=SpellCheckResponse)
async def spellcheck_endpoint(request: SpellCheckRequest):
    """텍스트의 맞춤법을 검사하고 수정합니다."""
    if not spellcheck_handler:
        raise HTTPException(status_code=503, detail="맞춤법 검사 핸들러가 초기화되지 않았습니다.")
    try:
        result = spellcheck_handler.create_spellcheck_response(
            request.text, request.auto_correct
        )
        return SpellCheckResponse.model_validate(result)
    except Exception as e:
        logger.error(f"❌ 맞춤법 검사 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="맞춤법 검사 중 오류가 발생했습니다.")


@app.get("/api/cost-status", response_model=CostStatusResponse)
async def get_cost_status():
    """월간 비용 사용 현황을 반환합니다."""
    usage_percentage = (
        (monthly_usage["cost"] / MONTHLY_BUDGET) * 100 if MONTHLY_BUDGET > 0 else 0
    )
    return CostStatusResponse(
        monthly_cost=monthly_usage["cost"],
        monthly_budget=MONTHLY_BUDGET,
        usage_percentage=usage_percentage,
        total_tokens=int(monthly_usage["tokens"]),
        cache_hits=0,  # TODO: 실제 캐시 히트 수 구현
    )


@app.get("/api/spellcheck/stats")
async def get_spellcheck_stats() -> ModuleStats:
    """맞춤법 검사기 통계를 반환합니다."""
    if not spellcheck_handler:
        raise HTTPException(status_code=503, detail="맞춤법 검사 핸들러가 초기화되지 않았습니다.")
    return spellcheck_handler.get_statistics()


@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "openai_client": "initialized" if openai_client else "not-initialized",
        "handlers": {
            "chat": "ok" if chat_handler else "fail",
            "spellcheck": "ok" if spellcheck_handler else "fail",
            "location": "ok" if location_handler else "fail",
            "web_search": "ok" if web_search_handler else "fail",
            "google_docs": "ok" if google_docs_handler else "fail",
        },
    }


@app.post("/api/location-suggest", response_model=LocationSuggestResponse)
async def suggest_locations(request: LocationSuggestRequest):
    """위치(도시/지역) 추천을 반환합니다."""
    if not location_handler:
        raise HTTPException(status_code=503, detail="위치 추천 핸들러가 초기화되지 않았습니다.")
    try:
        suggestions = location_handler.suggest_locations(request.query)
        return LocationSuggestResponse(suggestions=suggestions)
    except Exception as e:
        logger.error(f"❌ 위치 추천 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="위치 추천 처리 중 오류가 발생했습니다.")


@app.post("/api/web-search", response_model=WebSearchResponse)
async def web_search(request: WebSearchRequest):
    """웹 검색을 수행하고 결과를 반환합니다."""
    if not web_search_handler:
        raise HTTPException(status_code=503, detail="웹 검색 핸들러가 초기화되지 않았습니다.")

    start_time = datetime.now()
    try:
        summary, search_results = await web_search_handler.search(
            query=request.query,
            source=request.source,
            num_results=request.num_results,
            include_summary=request.include_summary,
        )

        # results 리스트의 각 항목을 WebSearchResult 모델로 변환
        validated_results = [
            WebSearchResult.model_validate(item) for item in search_results
        ]
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()

        return WebSearchResponse(
            query=request.query,
            source=request.source,
            num_results=len(validated_results),
            results=validated_results,
            summary=summary,
            timestamp=start_time.isoformat(),
            from_cache=False,  # TODO: 캐시 로직과 연동 필요
            response_time=response_time,
        )
    except Exception as e:
        logger.error(f"❌ 웹 검색 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="웹 검색 처리 중 오류가 발생했습니다.")


@app.get("/api/web-search/stats", response_model=WebSearchStatsResponse)
async def get_web_search_stats() -> WebSearchStatsResponse:
    """웹 검색 통계를 반환합니다."""
    if not web_search_handler:
        raise HTTPException(status_code=503, detail="웹 검색 핸들러가 초기화되지 않았습니다.")

    result = web_search_handler.get_statistics()
    return WebSearchStatsResponse.model_validate(result)


@app.delete("/api/web-search/cache")
async def clear_web_search_cache():
    """웹 검색 캐시를 삭제합니다."""
    if not web_search_handler:
        raise HTTPException(status_code=503, detail="웹 검색 핸들러가 초기화되지 않았습니다.")
    try:
        success = await web_search_handler.clear_cache()
        if success:
            return {"message": "웹 검색 캐시가 성공적으로 삭제되었습니다."}
        else:
            raise HTTPException(status_code=500, detail="캐시 삭제에 실패했습니다.")
    except Exception as e:
        logger.error(f"❌ 웹 검색 캐시 삭제 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="캐시 삭제 중 오류가 발생했습니다.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
