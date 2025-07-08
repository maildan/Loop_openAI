"""Web search API 라우터 모듈"""
# pyright: reportImportCycles=false
from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi import FastAPI

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:  # pragma: no cover
    from src.inference.api.handlers.web_search_handler import WebSearchHandler

from src.inference.api.schemas import (
    WebSearchRequest,
    WebSearchResponse,
    WebSearchStatsResponse,
)
from src.inference.api.schemas import WebSearchResult  # 타입 재사용

router = APIRouter()


@router.post("/api/web-search", response_model=WebSearchResponse)
async def web_search(request_body: WebSearchRequest, request: Request) -> WebSearchResponse:
    """웹 검색 엔드포인트"""
    app = cast(FastAPI, request.app)
    handler = cast("WebSearchHandler | None", getattr(app.state, "web_search_handler", None))
    if handler is None:
        raise HTTPException(status_code=503, detail="Web search handler not ready")

    start_time = time.time()
    summary, search_results = await handler.search(
        query=request_body.query,
        source=request_body.source,
        num_results=request_body.num_results,
        include_summary=request_body.include_summary,
    )
    end_time = time.time()

    validated_results = [WebSearchResult(**r) for r in search_results]
    # 타입 호환을 위해 List 타입으로 명시적 선언
    results_list: list[WebSearchResult] = validated_results

    return WebSearchResponse(
        query=request_body.query,
        source=request_body.source,
        num_results=len(results_list),
        results=results_list,
        summary=summary,
        timestamp=datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat(),
        from_cache=False,  # TODO: 캐시 동기화
        response_time=end_time - start_time,
    )


@router.get("/api/web-search/stats", response_model=WebSearchStatsResponse)
async def get_web_search_stats(request: Request) -> WebSearchStatsResponse:
    """웹 검색 통계 조회"""
    app = cast(FastAPI, request.app)
    handler = cast("WebSearchHandler | None", getattr(app.state, "web_search_handler", None))
    if handler is None:
        raise HTTPException(status_code=503, detail="Web search handler not ready")
    stats = handler.get_statistics()
    return WebSearchStatsResponse(
        total_searches=stats.get("total_searches", 0),
        cache_hits=stats.get("cache_hits", 0),
        cache_misses=stats.get("cache_misses", 0),
        avg_response_time=stats.get("avg_response_time", 0.0),
        last_search_time=stats.get("last_search_time"),
        cache_enabled=stats.get("cache_enabled", False),
    )


@router.delete("/api/web-search/cache")
async def clear_web_search_cache(request: Request):
    """웹 검색 캐시 삭제"""
    app = cast(FastAPI, request.app)
    handler = cast("WebSearchHandler | None", getattr(app.state, "web_search_handler", None))
    if handler is None:
        raise HTTPException(status_code=503, detail="Web search handler not ready")
    _ = await handler.clear_cache()  # bool 반환 무시를 명시적으로 처리
    return {"status": "Web search cache cleared"} 