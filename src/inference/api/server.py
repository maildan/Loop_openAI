#!/usr/bin/env python3
"""
Loop AI 모듈화된 추론 서버
맞춤법 검사 기능과 채팅 기능을 통합한 창작 지원 시스템
"""

import asyncio
import json
import logging
import os
import sys
import time
from collections import OrderedDict
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import re

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

# MCP 관련 임포트 추가
MCP_AVAILABLE = False
try:
    # MCP 라이브러리 임포트 시도
    import mcp
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ MCP 라이브러리 임포트 성공")
except ImportError as e:
    FastMCP = None
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ MCP 라이브러리 임포트 실패: {e}")

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# 로컬 모듈 import
try:
    from src.inference.api.handlers import ChatHandler, SpellCheckHandler
    from src.inference.api.handlers.location_handler import LocationHandler
    from src.inference.api.handlers.web_search_handler import WebSearchHandler
    from src.inference.api.handlers.google_docs_handler import GoogleDocsHandler
except ImportError as e:
    # 상대 import 실패 시 절대 import 시도
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
    from src.inference.api.handlers import ChatHandler, SpellCheckHandler
    from src.inference.api.handlers.location_handler import LocationHandler
    from src.inference.api.handlers.web_search_handler import WebSearchHandler
    from src.inference.api.handlers.google_docs_handler import GoogleDocsHandler

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Loop AI API", 
    description="Loop AI 창작 지원 시스템 - 채팅, 맞춤법 검사, 시놉시스 생성", 
    version="3.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000"],  # 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
openai_client: Optional[AsyncOpenAI] = None
chat_handler: Optional[ChatHandler] = None
spellcheck_handler: Optional[SpellCheckHandler] = None
location_handler: Optional[LocationHandler] = None
web_search_handler: Optional[WebSearchHandler] = None
google_docs_handler: Optional[GoogleDocsHandler] = None

# MCP 서버 설정
mcp_server = None
if MCP_AVAILABLE:
    try:
        # MCP 서버 초기화
        mcp_server = FastMCP("loop_ai", stateless_http=True)
        logger.info("✅ MCP 서버 초기화 완료")
    except Exception as e:
        logger.error(f"❌ MCP 서버 초기화 실패: {e}")
        mcp_server = None

# 비용 추적
PRICING_PER_TOKEN = {
    "gpt-4o-mini": {"input": 0.00015 / 1000, "output": 0.0006 / 1000},
    "gpt-4o": {"input": 0.005 / 1000, "output": 0.015 / 1000},
    "gpt-3.5-turbo": {"input": 0.0005 / 1000, "output": 0.0015 / 1000}
}

monthly_usage = {"cost": 0.0, "tokens": 0}
MONTHLY_BUDGET = float(os.getenv("OPENAI_MONTHLY_BUDGET", "15.0"))

# LRU 캐시 구현
class LRUCache:
    def __init__(self, capacity: int = 1024):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key: str) -> Optional[str]:
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: str) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        self.cache[key] = value

response_cache = LRUCache()

# API 모델 정의
class ChatMessage(BaseModel):
    role: str = Field(..., description="메시지 역할 (user/assistant)")
    content: str = Field(..., description="메시지 내용")

class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 메시지")
    history: List[ChatMessage] = Field(default=[], description="채팅 히스토리")
    model: Optional[str] = Field(None, description="사용할 모델")
    maxTokens: Optional[int] = Field(4000, description="최대 토큰 수")
    isLongForm: Optional[bool] = Field(False, description="긴 텍스트 생성 모드")
    continueStory: Optional[bool] = Field(False, description="이야기 계속하기 모드")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI 응답")
    model: str = Field(..., description="사용된 모델")
    cost: float = Field(..., description="비용 (USD)")
    tokens: int = Field(..., description="사용된 토큰 수")
    isComplete: Optional[bool] = Field(True, description="응답 완료 여부")
    continuationToken: Optional[str] = Field(None, description="계속하기 토큰")

class SpellCheckRequest(BaseModel):
    text: str = Field(..., description="맞춤법 검사할 텍스트")
    auto_correct: bool = Field(default=True, description="자동 수정 여부")

class SpellCheckResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    original_text: str = Field(..., description="원본 텍스트")
    corrected_text: str = Field(..., description="수정된 텍스트")
    errors_found: int = Field(..., description="발견된 오타 수")
    error_words: List[str] = Field(..., description="오타 단어 목록")
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
    suggestions: List[str] = Field(..., description="추천된 지역·도시명 목록")

class WebSearchRequest(BaseModel):
    query: str = Field(..., description="검색어")
    source: str = Field(default="web", description="검색 소스 (web, research, wiki, github, company)")
    num_results: int = Field(default=5, ge=1, le=10, description="결과 개수 (1-10)")
    include_summary: bool = Field(default=True, description="AI 요약 포함 여부")

class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    publishedDate: Optional[str] = None
    favicon: Optional[str] = None

class WebSearchResponse(BaseModel):
    query: str
    source: str
    num_results: int
    results: List[WebSearchResult]
    summary: str = ""
    timestamp: str
    from_cache: bool = False
    response_time: float

def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    """토큰 사용량 기반 비용 계산"""
    if model not in PRICING_PER_TOKEN:
        model = "gpt-4o-mini"  # 기본값
    
    pricing = PRICING_PER_TOKEN[model]
    input_cost = prompt_tokens * pricing["input"]
    output_cost = completion_tokens * pricing["output"]
    
    return input_cost + output_cost

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행되는 이벤트 핸들러"""
    global openai_client, chat_handler, spellcheck_handler, location_handler, web_search_handler, google_docs_handler
    
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
    
    # 데이터셋 로딩
    chat_handler.load_datasets()
    logger.info("✅ 모든 핸들러 및 데이터셋 초기화 완료")
    
    # MCP 서버 설정
    if MCP_AVAILABLE and mcp_server:
        # MCP 웹 검색 도구 등록
        @mcp_server.tool(name="mcp_web_search_startup")
        def mcp_web_search_startup_tool(query: str, num_results: int = 5):
            # 웹 검색 도구 구현
            try:
                if web_search_handler is not None:
                    loop = asyncio.get_event_loop()
                    results = loop.run_until_complete(
                        web_search_handler.search(query=query, num_results=min(num_results, 10))
                    )
                    if results and isinstance(results, dict):
                        return results.get("results", [])
                    return []
                return {"error": "Web search handler not initialized"}
            except Exception as e:
                logger.error(f"MCP 웹 검색 도구 오류: {e}")
                return {"error": str(e)}
        
        # MCP 앱 마운트
        app.mount("/mcp", mcp_server.streamable_http_app())
        logger.info("✅ MCP 서버 마운트 완료 (/mcp)")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Loop AI 서버가 실행 중입니다.",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    메인 채팅 엔드포인트. 사용자의 모든 메시지를 처리합니다.
    웹 검색, 창작, 맞춤법 등 모든 의도를 내부적으로 분기 처리합니다.
    """
    if not chat_handler:
        raise HTTPException(status_code=503, detail="채팅 핸들러가 아직 준비되지 않았습니다.")
    
    try:
        # Pydantic 모델을 dict 리스트로 변환
        history_dicts = [msg.dict() for msg in request.history]
        
        # 사용자 의도와 레벨 감지
        intent, level = chat_handler.detect_intent_and_level(request.message)
        
        if intent == "creation":
            # 창작 의도일 때는 generate_story_by_level 사용
            result = await chat_handler.generate_story_by_level(
                user_message=request.message,
                level=level,
                max_tokens=request.maxTokens or 4000,
                is_long_form=request.isLongForm or False,
                continue_story=request.continueStory or False
            )
        else:
            # 기타 의도일 때는 기본 handle_request 사용
            result = await chat_handler.handle_request(
                user_message=request.message,
                history=history_dicts
            )
        
        # 비용 및 토큰 추적
        cost = result.get("cost", 0)
        tokens = result.get("tokens", 0)
        monthly_usage["cost"] += cost
        monthly_usage["tokens"] += tokens
        
        return ChatResponse(
            response=result.get("response", "오류가 발생했습니다."),
            model=result.get("model", "N/A"),
            cost=cost,
            tokens=tokens,
            isComplete=result.get("isComplete", True),
            continuationToken=result.get("continuationToken", None)
        )
    except Exception as e:
        logger.error(f"채팅 처리 중 심각한 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {e}")

@app.post("/api/spellcheck", response_model=SpellCheckResponse)
async def spellcheck_endpoint(request: SpellCheckRequest):
    """맞춤법 검사 엔드포인트"""
    if not spellcheck_handler:
        raise HTTPException(status_code=503, detail="맞춤법 검사 핸들러가 준비되지 않았습니다.")
    
    try:
        result = spellcheck_handler.create_spellcheck_response(
            text=request.text, 
            auto_correct=request.auto_correct
        )
        return SpellCheckResponse(**result)
    except Exception as e:
        logger.error(f"맞춤법 검사 중 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cost-status", response_model=CostStatusResponse)
async def get_cost_status():
    """비용 상태 조회"""
    usage_percentage = (monthly_usage["cost"] / MONTHLY_BUDGET) * 100
    
    return CostStatusResponse(
        monthly_cost=monthly_usage["cost"],
        monthly_budget=MONTHLY_BUDGET,
        usage_percentage=usage_percentage,
        total_tokens=monthly_usage["tokens"],
        cache_hits=len(response_cache.cache)
    )

@app.get("/api/spellcheck/stats")
async def get_spellcheck_stats():
    """맞춤법 검사기 통계 정보"""
    if not spellcheck_handler:
        raise HTTPException(status_code=500, detail="맞춤법 검사 핸들러가 초기화되지 않았습니다")
    
    return spellcheck_handler.get_statistics()

@app.get("/api/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "openai_client_initialized": openai_client is not None,
        "chat_handler_initialized": chat_handler is not None
    }

# 위치 추천 전용 엔드포인트
@app.post("/api/location-suggest", response_model=LocationSuggestResponse)
async def suggest_locations(request: LocationSuggestRequest):
    """지역·도시명 추천 엔드포인트"""
    if not location_handler or not location_handler.enabled:
        raise HTTPException(status_code=503, detail="위치 추천 서비스를 사용할 수 없습니다")
    
    try:
        suggestions = location_handler.suggest_locations(request.query)
        return LocationSuggestResponse(suggestions=suggestions)
    except Exception as e:
        logger.error(f"위치 추천 오류: {e}")
        raise HTTPException(status_code=500, detail=f"위치 추천 중 오류가 발생했습니다: {str(e)}")

@app.post("/api/web-search", response_model=WebSearchResponse)
async def web_search(request: WebSearchRequest):
    """🔍 기가차드급 웹 검색 엔드포인트"""
    if not web_search_handler:
        raise HTTPException(status_code=503, detail="웹 검색 서비스를 사용할 수 없습니다")
    
    try:
        result = await web_search_handler.search(
            query=request.query,
            source=request.source,
            num_results=request.num_results,
            include_summary=request.include_summary
        )
        return WebSearchResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"웹 검색 오류: {e}")
        raise HTTPException(status_code=500, detail=f"웹 검색 중 오류가 발생했습니다: {str(e)}")

@app.get("/api/web-search/stats")
async def get_web_search_stats():
    """웹 검색 통계 조회"""
    if not web_search_handler:
        raise HTTPException(status_code=503, detail="웹 검색 서비스를 사용할 수 없습니다")
    
    return web_search_handler.get_statistics()

@app.delete("/api/web-search/cache")
async def clear_web_search_cache():
    """웹 검색 캐시 클리어"""
    if not web_search_handler:
        raise HTTPException(status_code=503, detail="웹 검색 서비스를 사용할 수 없습니다")
    
    success = await web_search_handler.clear_cache()
    return {"success": success, "message": "캐시가 클리어되었습니다" if success else "캐시 클리어에 실패했습니다"}

# Google Docs 관련 엔드포인트
@app.post("/api/docs/create")
async def create_document(title: str, content: str) -> Dict[str, Any]:
    """새로운 Google 문서 생성"""
    if not google_docs_handler:
        raise HTTPException(status_code=503, detail="Google Docs 서비스를 사용할 수 없습니다.")
    
    try:
        result = await google_docs_handler.create_document(title, content)
        return result
    except Exception as e:
        logger.error(f"문서 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/docs/{document_id}")
async def get_document(document_id: str) -> Dict[str, Any]:
    """문서 내용 가져오기"""
    if not google_docs_handler:
        raise HTTPException(status_code=503, detail="Google Docs 서비스를 사용할 수 없습니다.")
    
    try:
        document = await google_docs_handler.get_document(document_id)
        return document
    except Exception as e:
        logger.error(f"문서 가져오기 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/docs/{document_id}")
async def update_document(document_id: str, content: str) -> Dict[str, Any]:
    """문서 내용 업데이트"""
    if not google_docs_handler:
        raise HTTPException(status_code=503, detail="Google Docs 서비스를 사용할 수 없습니다.")
    
    try:
        result = await google_docs_handler.update_document(document_id, content)
        return result
    except Exception as e:
        logger.error(f"문서 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/docs/analyze")
async def analyze_document(document_id: str) -> Dict[str, Any]:
    """Google Docs 문서 분석"""
    if not google_docs_handler:
        raise HTTPException(status_code=503, detail="Google Docs 서비스를 사용할 수 없습니다.")
    
    try:
        analysis = await google_docs_handler.analyze_document(document_id)
        return analysis
    except Exception as e:
        logger.error(f"문서 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/docs/generate-story")
async def generate_story_from_doc(document_id: str, prompt: Optional[str] = None) -> Dict[str, Any]:
    """Google Docs 문서 기반으로 스토리 생성"""
    if not google_docs_handler or not chat_handler:
        raise HTTPException(status_code=503, detail="필요한 서비스를 사용할 수 없습니다.")
    
    try:
        # 문서 내용 추출
        content = await google_docs_handler.extract_document_content(document_id)
        
        # 프롬프트 생성
        base_prompt = f"""
다음 문서를 기반으로 새로운 이야기를 만들어주세요:

문서 내용:
{content[:1000]}  # 첫 1000자만 사용

원하는 스타일: {prompt if prompt else '자유롭게'}

이 문서의 주제와 내용을 참고하여 새롭고 창의적인 이야기를 만들어주세요.
"""
        
        # 스토리 생성 - handle_request 메소드 사용
        response = await chat_handler.handle_request(
            user_message=base_prompt,
            history=[]
        )
        
        return {
            "original_doc_id": document_id,
            "generated_story": response.get("generated_text", ""),
            "prompt_used": base_prompt
        }
        
    except Exception as e:
        logger.error(f"스토리 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 개발용 서버 실행
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    ) 