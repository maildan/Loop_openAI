#!/usr/bin/env python3
"""
Loop AI 모듈화된 추론 서버 (경량화 버전)
핸들러 초기화, lifespan, 미들웨어, 라우터 include만 담당합니다.
"""

from __future__ import annotations
import logging
import os
from collections import OrderedDict
from typing import TypeVar, Generic
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from openai import AsyncOpenAI

from src.inference.api.handlers import ChatHandler, SpellCheckHandler
from src.inference.api.handlers.location_handler import LocationHandler
from src.inference.api.handlers.web_search_handler import WebSearchHandler
from src.inference.api.handlers.assistant_handler import AssistantHandler

from src.inference.api.routes.spellcheck import router as spellcheck_router
from src.inference.api.routes.web_search import router as web_search_router
from src.inference.api.routes.assistant import router as assistant_router
from src.inference.api.routes.core import router as core_router
from src.inference.api.routes.location import router as location_router
from src.inference.api.routes.name_generator import router as name_router

# 가격 및 사용량 추적
PRICING_PER_TOKEN = {
    "gpt-4o-mini": {"input": 0.00015 / 1000, "output": 0.0006 / 1000},
    "gpt-4o": {"input": 0.005 / 1000, "output": 0.015 / 1000},
    "gpt-3.5-turbo": {"input": 0.0005 / 1000, "output": 0.0015 / 1000},
}
monthly_usage: dict[str, float] = {"cost": 0.0, "tokens": 0.0}
MONTHLY_BUDGET: float = float(os.getenv("OPENAI_MONTHLY_BUDGET", "15.0"))

# LRUCache 정의
K = TypeVar("K")
V = TypeVar("V")
class LRUCache(Generic[K, V]):
    capacity: int  # annotated class attribute for Pyright
    def __init__(self, capacity: int = 1024):
        self.cache: OrderedDict[K, V] = OrderedDict()
        self.capacity = capacity

    def get(self, key: K) -> V | None:
        val = self.cache.get(key)
        if val is None:
            return None
        self.cache.move_to_end(key)
        return val

    def put(self, key: K, value: V) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.capacity:
            _ = self.cache.popitem(last=False)  # explicitly ignore return value
        self.cache[key] = value

response_cache: LRUCache[str, str] = LRUCache()

# 전역 핸들러 변수
openai_client: AsyncOpenAI | None = None
chat_handler: ChatHandler | None = None
spellcheck_handler: SpellCheckHandler | None = None
location_handler: LocationHandler | None = None
web_search_handler: WebSearchHandler | None = None
assistant_handler: AssistantHandler | None = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """서버 시작 및 종료 이벤트 핸들러"""
    global openai_client, chat_handler, spellcheck_handler, location_handler, web_search_handler, assistant_handler
    logging.info("🚀 서버 시작")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.warning("⚠️ OPENAI_API_KEY 미설정")

    timeout = httpx.Timeout(10.0, connect=5.0)
    openai_client = AsyncOpenAI(api_key=api_key, timeout=timeout)
    chat_handler = ChatHandler(openai_api_key=api_key) if api_key else None
    spellcheck_handler = SpellCheckHandler(openai_client)
    location_handler = LocationHandler()
    web_search_handler = WebSearchHandler(openai_client)
    assistant_handler = AssistantHandler(openai_client, web_search_handler)

    app.state.chat_handler = chat_handler
    app.state.spellcheck_handler = spellcheck_handler
    app.state.location_handler = location_handler
    app.state.web_search_handler = web_search_handler
    app.state.assistant_handler = assistant_handler
    logging.info("✅ 핸들러 초기화 완료")
    yield
    logging.info("🌙 서버 종료")

app = FastAPI(
    title="Loop AI API",
    description="Loop AI 창작 지원 시스템",
    version="3.0.0",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 라우터 등록
app.include_router(spellcheck_router)
app.include_router(web_search_router)
app.include_router(assistant_router)
app.include_router(core_router)
app.include_router(location_router)
app.include_router(name_router)

if __name__ == "__main__":
    uvicorn.run("src.inference.api.newserver:app", host="0.0.0.0", port=8000, reload=True) 