"""Spellcheck 관련 라우터 모듈"""
# pyright: reportImportCycles=false

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from fastapi import APIRouter, HTTPException, Request
from fastapi import FastAPI

# 모델은 schemas 모듈에서 가져옴
from src.inference.api.schemas import SpellCheckRequest, SpellCheckResponse

from src.utils.spellcheck import ModuleStats

if TYPE_CHECKING:  # pragma: no cover
    from src.inference.api.handlers import SpellCheckHandler


router = APIRouter()


@router.post("/api/spellcheck", response_model=SpellCheckResponse)
async def spellcheck_endpoint(request_body: SpellCheckRequest, request: Request) -> SpellCheckResponse:  # noqa: D401
    """맞춤법 검사 또는 AI 교정을 수행합니다."""
    app = cast(FastAPI, request.app)
    spellcheck_handler = cast("SpellCheckHandler | None", getattr(app.state, "spellcheck_handler", None))
    if spellcheck_handler is None:
        raise HTTPException(status_code=503, detail="맞춤법 검사기 준비 안됨")

    try:
        if request_body.use_ai and request_body.full_document:
            # AI 기반 문맥 교정
            result = await spellcheck_handler.context_aware_correction(
                target_text=request_body.text, full_document=request_body.full_document
            )
        else:
            result = spellcheck_handler.create_spellcheck_response(
                request_body.text, request_body.auto_correct
            )

        return SpellCheckResponse(
            original_text=result.get("original_text", request_body.text),
            corrected_text=result.get("corrected_text", request_body.text),
            errors_found=result.get("errors_found", 0),
            error_words=result.get("error_words", []),
            accuracy=result.get("accuracy", 100.0),
            total_words=result.get("total_words", 0),
            reason=result.get("reason"),
            context_analysis=result.get("context_analysis"),
        )
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/spellcheck/stats", response_model=ModuleStats)
async def get_spellcheck_stats(request: Request) -> ModuleStats:
    """맞춤법 검사기 통계 조회"""
    app = cast(FastAPI, request.app)
    spellcheck_handler = cast("SpellCheckHandler | None", getattr(app.state, "spellcheck_handler", None))
    if spellcheck_handler is None:
        raise HTTPException(status_code=503, detail="맞춤법 검사기 준비 안됨")
    return spellcheck_handler.get_statistics() 