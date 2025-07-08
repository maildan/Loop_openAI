"""Core 시스템 엔드포인트 라우터
- 루트, 헬스체크, 비용 상태, 캐시 초기화
"""
# pyright: reportImportCycles=false
from __future__ import annotations

from datetime import datetime, timezone
from typing import cast, TYPE_CHECKING

from fastapi import APIRouter, FastAPI, Request

from src.inference.api.schemas import CostStatusResponse
from src.inference.api.server import response_cache, MONTHLY_BUDGET, monthly_usage

if TYPE_CHECKING:
    from src.inference.api.handlers.web_search_handler import WebSearchHandler

router = APIRouter()

@router.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Loop AI 서버가 실행 중입니다."}


@router.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "ok",
        "version": "3.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/cost-status", response_model=CostStatusResponse)
async def get_cost_status():
    """월별 비용 현황"""
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


@router.post("/api/clear_cache")
async def clear_cache_endpoint(request: Request):
    """내부 캐시 초기화"""
    app = cast(FastAPI, request.app)
    web_search_handler = cast("WebSearchHandler | None", getattr(app.state, "web_search_handler", None))
    if web_search_handler:
        _ = await web_search_handler.clear_cache()

    response_cache.cache.clear()
    return {"status": "all caches cleared"} 