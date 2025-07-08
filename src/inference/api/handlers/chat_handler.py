"""
Loop AI 채팅 처리 핸들러 - Jane Friedman 3단계 프롬프트 방법론 적용
1. Build Stamina Through Practice (실습을 통한 체력 구축)
2. Develop Mastery of Techniques (기법 숙련도 개발)
3. Apply Prompts to Projects (프로젝트에 적용)
"""

import openai
import json
from openai import AsyncOpenAI
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# 프롬프트 로더를 Jinja2 기반 shared loader로 변경
from src.shared.prompts.loader import get_prompt

class ChatRequest(BaseModel):
    """
    /api/chat 엔드포인트에 대한 요청 모델입니다.
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="사용자가 입력한 메시지 또는 스토리 생성 요청",
        examples=["우주를 여행하는 고양이에 대한 이야기를 써줘"]
    )
    max_tokens: int | None = Field(
        None,
        ge=50,
        description="응답에 사용할 최대 토큰 수. 지정하지 않으면 800, 최대 128000으로 제한",
    )

class ChatHandler:
    """
    채팅 관련 API 요청을 처리하는 핸들러 클래스입니다.
    의도 분류 및 스토리 생성을 담당합니다.
    """
    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            # HTTPException 사용으로 unused import 해결
            raise HTTPException(status_code=500, detail="OpenAI API 키가 필요합니다.")

        # openai 모듈 사용 예시 (unused import 해결)
        openai.api_key = openai_api_key

        # 속성 타입 주석 추가
        self.client: AsyncOpenAI = AsyncOpenAI(api_key=openai_api_key)
        self.router: APIRouter = APIRouter()
        self.router.add_api_route("/api/chat", self.handle_chat, methods=["POST"], response_model=None)

    async def _get_intent(self, user_message: str) -> str:
        """사용자 메시지로부터 의도를 분류합니다."""
        # prompt key corrected to 'intent_classifier'
        prompt = get_prompt('intent_classifier', user_message=user_message)
        if not prompt:
            return "story_generation"  # Fallback

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=20,
                stream=False
            )
            content = response.choices[0].message.content
            if content:
                intent = content.strip().lower()
                return "greeting" if "greeting" in intent else "story_generation"
            return "story_generation" # 응답 내용이 없는 경우 기본값
        except Exception as e:
            print(f"의도 분류 API 호출 오류: {e}")
            return "story_generation"

    async def _stream_static_message(self, message_key: str):
        """정적인 메시지를 SSE 형식으로 스트리밍합니다."""
        message = get_prompt(message_key)
        content_json = json.dumps({"type": "message", "content": message}, ensure_ascii=False)
        yield f"data: {content_json}\n\n"
        
        end_stream_json = json.dumps({"type": "end", "reason": "completed"}, ensure_ascii=False)
        yield f"data: {end_stream_json}\n\n"

    async def _stream_story(self, user_message: str):
        """LLM을 통해 생성된 스토리를 SSE 형식으로 스트리밍합니다."""
        prompt = get_prompt('story_generation', user_message=user_message)
        if not prompt:
            error_json = json.dumps({"type": "error", "content": "스토리 생성 프롬프트를 찾을 수 없습니다."})
            yield f"data: {error_json}\n\n"
            return

        try:
            stream = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                stream=True
            )
            
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    content_json = json.dumps({"type": "chunk", "content": content}, ensure_ascii=False)
                    yield f"data: {content_json}\n\n"
            
            end_stream_json = json.dumps({"type": "end", "reason": "completed"}, ensure_ascii=False)
            yield f"data: {end_stream_json}\n\n"

        except Exception as e:
            error_message = f"API 호출 중 오류 발생: {str(e)}"
            error_json = json.dumps({"type": "error", "content": error_message}, ensure_ascii=False)
            yield f"data: {error_json}\n\n"

    async def handle_chat(self, request: ChatRequest):
        """
        메인 채팅 핸들러입니다.
        의도를 파악하고 적절한 스트리밍 응답을 반환합니다.
        """
        user_message = request.message
        intent = await self._get_intent(user_message)

        if intent == "greeting":
            return StreamingResponse(
                self._stream_static_message('greeting_response'),
                media_type="text/event-stream"
            )
        # Non-streaming full story response
        try:
            prompt = get_prompt('story_generation', user_message=user_message)
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=min(request.max_tokens or 800, 128000),
                stream=False,
            )
            story = response.choices[0].message.content or ""
            return {"content": story}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"스토리 생성 중 오류: {e}")
