"""AI Assistant 관련 엔드포인트 라우터
- 플롯 홀 탐지, 캐릭터 일관성, 클리프행어, 독자 반응 예측 등
"""
# pyright: reportImportCycles=false
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from fastapi import APIRouter, HTTPException, Request, FastAPI

# Typed import (순환 방지)
from src.inference.api.schemas import (
    SentenceImprovementRequest,
    SentenceImprovementResponse,
    PlotHoleDetectionRequest,
    PlotHoleDetectionResponse,
    CharacterConsistencyRequest,
    CharacterConsistencyResponse,
    CliffhangerRequest,
    CliffhangerResponse,
    CliffhangerSuggestion,
    ReaderResponseRequest,
    ReaderResponseResponse,
    SmartSentenceImprovementRequest,
    SmartSentenceImprovementResponse,
    EpisodeLengthRequest,
    EpisodeLengthResponse,
    BetaReadRequest,
    BetaReadResponse,
    TrendAnalysisRequest,
    TrendAnalysisResponse,
)

if TYPE_CHECKING:  # pragma: no cover
    from src.inference.api.handlers.assistant_handler import AssistantHandler

logger = logging.getLogger(__name__)

router = APIRouter()

# --- 문장 개선 ---
@router.post("/api/improve-sentence", response_model=SentenceImprovementResponse)
async def improve_sentence_endpoint(request_body: SentenceImprovementRequest, request: Request) -> SentenceImprovementResponse:  # noqa: D401
    """AI를 사용하여 단일 문장을 다각도로 개선합니다."""
    app = cast(FastAPI, request.app)
    assistant_handler = cast("AssistantHandler | None", getattr(app.state, "assistant_handler", None))
    if assistant_handler is None:
        raise HTTPException(status_code=503, detail="Assistant handler not initialized")

    try:
        result = await assistant_handler.improve_sentence(
            original_sentence=request_body.original_sentence,
            genre=request_body.genre,
            character_profile=request_body.character_profile,
            context=request_body.context,
            model=request_body.model,
        )
        suggestions_dict = {
            "vivid": result["vivid_sentence"],
            "concise": result["concise_sentence"],
            "character_voice": result["character_voice_sentence"],
        }
        return SentenceImprovementResponse(
            suggestions=suggestions_dict,
            model=result["model"],
            cost=result["cost"],
            tokens=result["tokens"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover
        logger.exception("문장 개선 처리 중 예외", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- 플롯 홀 탐지 ---
@router.post(
    "/api/v1/story/analyze/plot-holes",
    response_model=PlotHoleDetectionResponse,
    tags=["AI Assistant"],
    summary="실시간 플롯 홀 감지",
)
async def detect_plot_holes_endpoint(request_body: PlotHoleDetectionRequest, request: Request) -> PlotHoleDetectionResponse:
    app = cast(FastAPI, request.app)
    assistant_handler = cast("AssistantHandler | None", getattr(app.state, "assistant_handler", None))
    if assistant_handler is None:
        raise HTTPException(status_code=503, detail="Assistant handler not initialized")

    try:
        result = await assistant_handler.detect_plot_holes(
            full_story_text=request_body.full_story_text,
            model=request_body.model,
        )
        return PlotHoleDetectionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover
        logger.exception("플롯 홀 감지 중 예외", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- 캐릭터 일관성 ---
@router.post(
    "/api/v1/story/analyze/character-consistency",
    response_model=CharacterConsistencyResponse,
    tags=["AI Assistant"],
    summary="캐릭터 일관성 체크",
)
async def check_character_consistency_endpoint(request_body: CharacterConsistencyRequest, request: Request) -> CharacterConsistencyResponse:
    app = cast(FastAPI, request.app)
    assistant_handler = cast("AssistantHandler | None", getattr(app.state, "assistant_handler", None))
    if assistant_handler is None:
        raise HTTPException(status_code=503, detail="Assistant handler not initialized")

    try:
        result = await assistant_handler.check_character_consistency(
            character_name=request_body.character_name,
            personality=request_body.personality,
            speech_style=request_body.speech_style,
            core_values=request_body.core_values,
            other_settings=request_body.other_settings,
            story_text_for_analysis=request_body.story_text_for_analysis,
            model=request_body.model,
        )
        return CharacterConsistencyResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover
        logger.exception("캐릭터 일관성 검증 중 예외", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- 클리프행어 생성 ---
@router.post(
    "/api/v1/story/generate/cliffhanger",
    response_model=CliffhangerResponse,
    tags=["AI Assistant"],
    summary="지능형 클리프행어 생성기",
)
async def generate_cliffhanger_endpoint(request_body: CliffhangerRequest, request: Request) -> CliffhangerResponse:
    app = cast(FastAPI, request.app)
    assistant_handler = cast("AssistantHandler | None", getattr(app.state, "assistant_handler", None))
    if assistant_handler is None:
        raise HTTPException(status_code=503, detail="Assistant handler not initialized")

    try:
        result = await assistant_handler.generate_cliffhanger(
            genre=request_body.genre,
            scene_context=request_body.scene_context,
            model=request_body.model,
        )
        suggestions_list = [CliffhangerSuggestion(**item) for item in result.get("suggestions", [])]
        return CliffhangerResponse(
            suggestions=suggestions_list,
            model=result.get("model", "unknown"),
            cost=result.get("cost", 0.0),
            tokens=result.get("tokens", 0),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover
        logger.exception("클리프행어 생성 중 예외", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- 독자 반응 예측 ---
@router.post(
    "/api/v1/story/predict/reader-response",
    response_model=ReaderResponseResponse,
    tags=["AI Assistant"],
    summary="독자 반응 예측 AI",
)
async def predict_reader_response_endpoint(request_body: ReaderResponseRequest, request: Request) -> ReaderResponseResponse:
    app = cast(FastAPI, request.app)
    assistant_handler = cast("AssistantHandler | None", getattr(app.state, "assistant_handler", None))
    if assistant_handler is None:
        raise HTTPException(status_code=503, detail="Assistant handler not initialized")

    try:
        result = await assistant_handler.predict_reader_response(
            platform=request_body.platform,
            scene_context=request_body.scene_context,
            model=request_body.model,
        )
        return ReaderResponseResponse(
            prediction_report=result.get("prediction_report", {}),
            model=result.get("model", "unknown"),
            cost=result.get("cost", 0.0),
            tokens=result.get("tokens", 0),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover
        logger.exception("독자 반응 예측 중 예외", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- 스마트 문장 개선 ---
@router.post(
    "/api/v1/story/analyze/sentence-improvement",
    response_model=SmartSentenceImprovementResponse,
    tags=["AI Assistant"],
    summary="스마트 문장 개선",
)
async def smart_sentence_improvement_endpoint(request_body: SmartSentenceImprovementRequest, request: Request) -> SmartSentenceImprovementResponse:
    app = cast(FastAPI, request.app)
    assistant_handler = cast("AssistantHandler | None", getattr(app.state, "assistant_handler", None))
    if assistant_handler is None:
        raise HTTPException(status_code=503, detail="Assistant handler not initialized")

    try:
        result = await assistant_handler.run_smart_sentence_improvement(
            original_text=request_body.original_text,
            model=request_body.model,
        )
        return SmartSentenceImprovementResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover
        logger.exception("스마트 문장 개선 중 예외", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- 에피소드 길이 최적화 ---
@router.post(
    "/api/v1/story/optimize/episode-length",
    response_model=EpisodeLengthResponse,
    tags=["AI Assistant"],
    summary="에피소드 길이 최적화",
)
async def optimize_episode_length_endpoint(request_body: EpisodeLengthRequest, request: Request) -> EpisodeLengthResponse:
    app = cast(FastAPI, request.app)
    assistant_handler = cast("AssistantHandler | None", getattr(app.state, "assistant_handler", None))
    if assistant_handler is None:
        raise HTTPException(status_code=503, detail="Assistant handler not initialized")

    try:
        result = await assistant_handler.optimize_episode_length(
            platform=request_body.platform,
            episode_text=request_body.episode_text,
            model=request_body.model,
        )
        return EpisodeLengthResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover
        logger.exception("에피소드 길이 최적화 중 예외", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- 베타 리딩 ---
@router.post(
    "/api/v1/story/analyze/beta-read",
    response_model=BetaReadResponse,
    tags=["AI Assistant"],
    summary="AI 베타리더 종합 분석",
)
async def request_beta_read_endpoint(request_body: BetaReadRequest, request: Request) -> BetaReadResponse:
    app = cast(FastAPI, request.app)
    assistant_handler = cast("AssistantHandler | None", getattr(app.state, "assistant_handler", None))
    if assistant_handler is None:
        raise HTTPException(status_code=503, detail="Assistant handler not initialized")

    try:
        result = await assistant_handler.get_beta_read_feedback(
            manuscript=request_body.manuscript,
            genre=request_body.genre,
            target_audience=request_body.target_audience,
            author_concerns=request_body.author_concerns,
            model=request_body.model,
        )
        return BetaReadResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover
        logger.exception("베타 리딩 요청 중 예외", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --- 트렌드 분석 ---
@router.post(
    "/api/v1/story/analyze/trends",
    response_model=TrendAnalysisResponse,
    tags=["AI Assistant"],
    summary="웹소설 트렌드 분석 및 적용",
)
async def analyze_trends_endpoint(request_body: TrendAnalysisRequest, request: Request) -> TrendAnalysisResponse:
    app = cast(FastAPI, request.app)
    assistant_handler = cast("AssistantHandler | None", getattr(app.state, "assistant_handler", None))

    if assistant_handler is None:
        raise HTTPException(status_code=503, detail="Assistant handler not initialized")

    try:
        result = await assistant_handler.analyze_trends(
            genre=request_body.genre,
            synopsis=request_body.synopsis,
            keywords=request_body.keywords,
            platform=request_body.platform,
            model=request_body.model,
        )
        # searched_data 타입 캐스팅 처리
        searched_data: list[dict[str, object]] = [dict(item) for item in result.get("searched_data", [])]
        return TrendAnalysisResponse(
            trend_report=result.get("trend_report", ""),
            model=result.get("model", "unknown"),
            cost=result.get("cost", 0.0),
            tokens=result.get("tokens", 0),
            searched_data=searched_data,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # pragma: no cover
        logger.exception("트렌드 분석 중 예외", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal Server Error") 