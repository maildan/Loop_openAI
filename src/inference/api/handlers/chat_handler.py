# pyright: reportAny=false, reportExplicitAny=false, reportRedeclaration=false
"""
Loop AI 채팅 처리 핸들러 - Jane Friedman 3단계 프롬프트 방법론 적용
1. Build Stamina Through Practice (실습을 통한 체력 구축)
2. Develop Mastery of Techniques (기법 숙련도 개발)
3. Apply Prompts to Projects (프로젝트에 적용)
"""

import openai
import json
from openai import AsyncOpenAI
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import cast
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai import RateLimitError

# 타입 안전성을 위해 핸들러 타입을 가져옵니다
from src.inference.api.handlers.spellcheck_handler import SpellCheckHandler
from src.inference.api.handlers.location_handler import LocationHandler
from src.inference.api.handlers.web_search_handler import WebSearchHandler
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
                messages=cast(list[ChatCompletionMessageParam], [{"role": "user", "content": prompt}]),
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
                messages=cast(list[ChatCompletionMessageParam], [{"role": "user", "content": prompt}]),
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

    async def handle_chat(self, chat_request: ChatRequest, request: Request):
        """
        메인 채팅 핸들러입니다.
        의도를 파악하고 적절한 스트리밍 응답을 반환합니다.
        """
        # 사용자 입력 및 사용자 식별
        user_message = chat_request.message.strip()
        try:
            client = request.client
            user_id = request.headers.get("X-User-Id") or (client.host if client else "anonymous")
            # FastAPI 앱 타입 캐스트로 state 접근
            from fastapi import FastAPI
            app_instance = cast(FastAPI, request.app)
            # 1. 이름 생성 기능 분기
            import re
            if "이름" in user_message:
                # 개수, 성별, 스타일 추출
                count_match = re.search(r"(\d+)개", user_message)
                count = int(count_match.group(1)) if count_match else 5
                gender = "female" if "여자" in user_message else ("male" if "남자" in user_message else None)
                style = "fantasy" if "판타지" in user_message else None
                from src.utils.name_generator import generate_multiple_names
                result = {"names": generate_multiple_names(count=count, gender=gender, style=style)}
                # 자연스러운 후속 대화 생성
                system_msg = get_prompt("system_prompt")
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "assistant", "content": json.dumps(result, ensure_ascii=False)},
                    {"role": "user", "content": "위 결과를 바탕으로 자연스럽게 대화를 이어가주세요."},
                ]
                # messages를 적절한 타입으로 캐스트
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=cast(list[ChatCompletionMessageParam], messages),
                    temperature=0.7,
                    stream=False,
                    user=user_id,
                )
                reply = response.choices[0].message.content or ""
                return {"result": result, "reply": reply}
            # 2. 맞춤법 검사 분기
            if "맞춤법" in user_message:
                # state를 통해 핸들러 가져오기
                spellcheck = cast(SpellCheckHandler, app_instance.state.spellcheck_handler)
                result = spellcheck.check_text(user_message)
                payload = {"original": result["original"], "corrected": result["corrected"]}
                # 자연스러운 후속 대화 생성
                system_msg = get_prompt("system_prompt")
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "assistant", "content": json.dumps(payload, ensure_ascii=False)},
                    {"role": "user", "content": "맞춤법 검사 결과를 바탕으로 간단히 코멘트 부탁해요."},
                ]
                # messages를 적절한 타입으로 캐스트
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=cast(list[ChatCompletionMessageParam], messages),
                    temperature=0.7,
                    stream=False,
                    user=user_id,
                )
                reply = response.choices[0].message.content or ""
                return {"result": payload, "reply": reply}
            # 3. 위치 추천 분기
            if any(k in user_message for k in ["위치", "장소"]):
                count_match = re.search(r"(\d+)개", user_message)
                limit = int(count_match.group(1)) if count_match else 5
                # state를 통해 핸들러 가져오기
                location = cast(LocationHandler, app_instance.state.location_handler)
                suggestions = await location.suggest_locations(user_message, limit)
                payload = {"suggestions": suggestions}
                # 자연스러운 후속 대화 생성
                system_msg = get_prompt("system_prompt")
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "assistant", "content": json.dumps(payload, ensure_ascii=False)},
                    {"role": "user", "content": "추천된 위치에 대해 간단히 설명해줘."},
                ]
                # messages를 적절한 타입으로 캐스트
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=cast(list[ChatCompletionMessageParam], messages),
                    temperature=0.7,
                    stream=False,
                    user=user_id,
                )
                reply = response.choices[0].message.content or ""
                return {"result": payload, "reply": reply}
            # 4. 웹 검색 분기
            if "검색" in user_message or "알려줘" in user_message:
                count_match = re.search(r"(\d+)개", user_message)
                num = int(count_match.group(1)) if count_match else 5
                # state를 통해 핸들러 가져오기
                websearch = cast(WebSearchHandler, app_instance.state.web_search_handler)
                _, results = await websearch.search(user_message, num_results=num, include_summary=False)
                payload = {"results": results}
                # 자연스러운 후속 대화 생성
                system_msg = get_prompt("system_prompt")
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "assistant", "content": json.dumps(payload, ensure_ascii=False)},
                    {"role": "user", "content": "검색 결과를 요약해서 알려줘."},
                ]
                # messages를 적절한 타입으로 캐스트
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=cast(list[ChatCompletionMessageParam], messages),
                    temperature=0.7,
                    stream=False,
                    user=user_id,
                )
                reply = response.choices[0].message.content or ""
                return {"result": payload, "reply": reply}
            # 기존 의도 분기
            intent = await self._get_intent(user_message)

            if intent == "greeting":
                return StreamingResponse(
                    self._stream_static_message('greeting_response'),
                    media_type="text/event-stream"
                )
            # Non-streaming full story response
            prompt = get_prompt('story_generation', user_message=user_message)
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=cast(list[ChatCompletionMessageParam], [{"role": "user", "content": prompt}]),
                temperature=0.7,
                # 최대 토큰을 128000으로 설정하여 스토리가 중간에 잘리지 않도록 합니다
                max_tokens=chat_request.max_tokens or 128000,
                stream=False,
                user=user_id,
            )
            story = response.choices[0].message.content or ""
            return {"content": story}
        except RateLimitError:
            raise HTTPException(status_code=429, detail="OpenAI 할당량을 초과했습니다. 사용량 및 결제 정보를 확인하세요.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"스토리 생성 중 오류: {e}")
