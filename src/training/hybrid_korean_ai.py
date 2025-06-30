import os
from typing import Any, Callable, cast, TypedDict

import requests
import streamlit as st

# OpenAI 가져오기 (선택적)
try:
    import openai
    # OpenAI의 CompletionCreate과 같은 타입을 직접 사용하기 위함
    from openai.types.chat import ChatCompletionMessageParam

    openai_available = True
except ImportError:
    openai_available = False
    openai = None
    ChatCompletionMessageParam = None  # type: ignore


class ModelInfo(TypedDict):
    name: str
    type: str
    cost: str


class ChatMessage(TypedDict):
    role: str
    content: str

# --- Ollama API 응답을 위한 TypedDict ---
class OllamaModel(TypedDict):
    name: str
    model: str
    modified_at: str
    size: int
    digest: str
    details: dict[str, Any]

class OllamaTagsResponse(TypedDict):
    models: list[OllamaModel]

class OllamaChatResponseMessage(TypedDict):
    role: str
    content: str

class OllamaChatResponse(TypedDict):
    model: str
    created_at: str
    message: OllamaChatResponseMessage
    done: bool


class HybridKoreanAI:
    def __init__(self) -> None:
        self.openai_key: str | None = os.getenv("OPEN_API_KEY") or os.getenv(
            "OPENAI_API_KEY"
        )
        if not self.openai_key:
            try:
                self.openai_key = st.secrets.get("OPENAI_API_KEY", "")
            except Exception:
                self.openai_key = ""

        self.use_openai: bool = bool(self.openai_key) and openai_available

        if self.use_openai and openai:
            openai.api_key = self.openai_key

    def get_available_models(self) -> dict[str, ModelInfo]:
        models: dict[str, ModelInfo] = {}
        if self.use_openai:
            models.update(
                {
                    "gpt-4o-mini": {
                        "name": "GPT-4o Mini (OpenAI)",
                        "type": "api",
                        "cost": "$0.15/M input, $0.60/M output",
                    },
                    "gpt-4-turbo": {
                        "name": "GPT-4 Turbo (OpenAI)",
                        "type": "api",
                        "cost": "$10/M input, $30/M output",
                    },
                }
            )

        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                local_models_response: OllamaTagsResponse = response.json()
                local_models = local_models_response.get("models", [])
                for model in local_models:
                    model_name = model.get("name", "unknown")
                    models[f"local_{model_name}"] = {
                        "name": f"{model_name} (로컬)",
                        "type": "local",
                        "cost": "무료",
                    }
        except requests.RequestException:
            pass  # 로컬 모델을 사용할 수 없는 경우 조용히 실패
        return models

    def generate_response(
        self,
        model: str,
        messages: list[ChatMessage],
        temperature: float,
        progress_callback: Callable[[int, str], None],
    ) -> str:
        model_info = self.get_available_models().get(model)
        if not model_info:
            return "오류: 모델을 찾을 수 없습니다."

        try:
            if model_info["type"] == "api":
                if not (self.use_openai and openai and ChatCompletionMessageParam):
                    return "오류: OpenAI 라이브러리가 없거나 API 키가 설정되지 않았습니다."
                progress_callback(10, "OpenAI API 호출 중...")

                # messages 타입을 ChatCompletionMessageParam 리스트로 캐스팅
                typed_messages = cast(list[ChatCompletionMessageParam], messages)

                response = openai.chat.completions.create(
                    model=model,
                    messages=typed_messages,
                    temperature=temperature,
                    stream=True,
                )

                full_response = ""
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                progress_callback(100, "완료")
                return full_response

            elif model_info["type"] == "local":
                progress_callback(10, "로컬 모델 호출 중...")
                actual_model_name = model.replace("local_", "")
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": actual_model_name,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": temperature},
                    },
                    timeout=120,
                )
                response.raise_for_status()
                progress_callback(100, "완료")
                response_data: OllamaChatResponse = response.json()
                return response_data.get("message", {"content": ""}).get("content", "")

        except requests.RequestException as e:
            return f"오류: 로컬 모델 연결 실패 - {e}"
        except Exception as e:
            if openai and isinstance(e, openai.APIError):
                return f"오류: OpenAI API 문제 발생 - {e}"
            return f"오류: 생성 중 문제 발생 - {e}"
        return "오류: 알 수 없는 모델 타입"


def initialize_session_state() -> None:
    """Streamlit 세션 상태 초기화"""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main_page(ai: HybridKoreanAI, available_models: dict[str, ModelInfo]) -> None:
    _ = st.set_page_config(page_title="하이브리드 AI", layout="centered")
    _ = st.title("🔀 하이브리드 한국어 AI")

    initialize_session_state()

    # --- 사이드바 ---
    with st.sidebar:
        _ = st.header("⚙️ 설정")
        model_options = list(available_models.keys())

        if not model_options:
            _ = st.warning("사용 가능한 모델이 없습니다. Ollama를 실행하거나 OpenAI 키를 설정하세요.")
            st.stop()

        selected_model = st.selectbox(
            "모델 선택",
            options=model_options,
            format_func=lambda x: str(available_models.get(x, {"name": x}).get("name", x)),
        )

        temperature = st.slider("창의성 (Temperature)", 0.0, 1.0, 0.7, 0.05)

        _ = st.header("대화 기록")
        if st.button("새 대화 시작"):
            st.session_state.messages = []
            st.rerun()

    # --- 채팅 인터페이스 ---
    messages = cast(list[ChatMessage], st.session_state.messages)
    for message in messages:
        with st.chat_message(message["role"]):
            _ = st.markdown(message["content"])

    if prompt := st.chat_input("무엇을 도와드릴까요?"):
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            _ = st.markdown(prompt)

        with st.chat_message("assistant"):
            progress_bar = st.progress(0, "AI가 생각 중...")

            def progress_callback(progress: int, text: str) -> None:
                progress_bar.progress(progress, text)

            if selected_model:
                response_content = ai.generate_response(
                    model=selected_model,
                    messages=messages,
                    temperature=temperature,
                    progress_callback=progress_callback,
                )
                _ = st.markdown(response_content)
                messages.append({"role": "assistant", "content": response_content})
            else:
                _ = st.warning("모델을 선택해주세요.")


if __name__ == "__main__":
    ai_instance = HybridKoreanAI()
    models = ai_instance.get_available_models()
    main_page(ai_instance, models) 