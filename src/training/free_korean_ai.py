import streamlit as st
import requests
import json
import subprocess
from datetime import datetime
from typing import Generator, Any, TypedDict, cast, Literal


# --- 타입 정의 ---
class OllamaModelInfo(TypedDict):
    name: str
    size: str
    quality: str
    speed: str


class OllamaListModel(TypedDict):
    name: str
    # 기타 ollama list가 반환하는 필드들...


class StreamlitSessionState(TypedDict):
    """Streamlit 세션 상태 타입"""
    messages: list[dict[Literal["role", "content"], str]]
    last_response: str


# 로컬 모델 설정
AVAILABLE_MODELS: dict[str, OllamaModelInfo] = {
    "solar:10.7b-instruct-v1-q4_K_M": {
        "name": "SOLAR 10.7B (한국어 특화)",
        "size": "6.4GB",
        "quality": "⭐⭐⭐⭐⭐",
        "speed": "빠름",
    },
    "qwen2.5:7b-instruct-q4_K_M": {
        "name": "Qwen2.5 7B (다국어)",
        "size": "4.4GB",
        "quality": "⭐⭐⭐⭐",
        "speed": "매우 빠름",
    },
    "gemma2:2b-instruct-q4_K_M": {
        "name": "Gemma2 2B (최경량)",
        "size": "1.7GB",
        "quality": "⭐⭐⭐",
        "speed": "초고속",
    },
}


def check_ollama_installed() -> bool:
    """Ollama 설치 확인"""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_ollama_guide() -> None:
    """Ollama 설치 가이드"""
    _ = st.error("🚨 Ollama가 설치되지 않았습니다!")

    _ = st.markdown(
        """
    ### 📥 Ollama 설치 방법 (5분)
    
    #### macOS:
    ```bash
    brew install ollama
    ```
    
    #### Linux:
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
    
    #### Windows:
    1. https://ollama.com/download 에서 다운로드
    2. 설치 후 터미널 재시작
    
    ### 🔄 설치 후 할 일:
    ```bash
    # 1. Ollama 서비스 시작
    ollama serve
    
    # 2. 한국어 모델 다운로드 (새 터미널에서)
    ollama pull solar:10.7b-instruct-v1-q4_K_M
    ```
    """
    )

    if st.button("🔄 새로고침 (설치 후 클릭)"):
        st.rerun()


def get_available_models() -> list[str]:
    """설치된 모델 목록 가져오기"""
    try:
        # JSON 형식으로 출력 요청
        result = subprocess.run(
            ["ollama", "list", "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            models_data = [
                json.loads(line) for line in result.stdout.strip().split("\n")
            ]
            typed_models = cast(list[OllamaListModel], models_data)
            return [model["name"] for model in typed_models]
        return []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def download_model(model_name: str) -> bool:
    """모델 다운로드"""
    try:
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        # 실시간 진행상황 표시
        progress_placeholder = st.empty()

        while True:
            if process.stdout is not None:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    _ = progress_placeholder.text(f"다운로드 중: {output.strip()}")
            else:
                break

        return process.wait() == 0
    except FileNotFoundError:
        st.error("Ollama 명령어를 찾을 수 없습니다. 설치를 확인해주세요.")
        return False
    except Exception as e:
        st.error(f"모델 다운로드 중 오류 발생: {e}")
        return False


def generate_with_ollama(
    prompt: str, model: str, temperature: float
) -> Generator[str, None, None]:
    """Ollama로 한국어 생성 (스트리밍)"""
    try:
        korean_prompt = f"""당신은 한국어 창작 전문가입니다.

요청: {prompt}

자연스럽고 창의적인 한국어로 창작해주세요. 한국적 정서와 문화를 반영하여 흥미로운 이야기를 만들어주세요."""

        response_stream = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": korean_prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9,
                    "num_predict": 1024,
                },
            },
            stream=True,
            timeout=120,
        )
        response_stream.raise_for_status()

        for line in response_stream.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    yield chunk.get("response", "")
                    if chunk.get("done"):
                        break
                except json.JSONDecodeError:
                    continue  # 가끔 빈 줄이나 불완전한 JSON이 올 수 있음

    except requests.exceptions.ConnectionError:
        yield "❌ Ollama 서버에 연결할 수 없습니다. 'ollama serve' 명령으로 서버를 시작해주세요."
    except requests.exceptions.RequestException as e:
        yield f"API 요청 중 오류 발생: {e}"
    except Exception as e:
        yield f"알 수 없는 오류 발생: {str(e)}"


def main() -> None:
    """메인 애플리케이션 함수"""
    st.set_page_config(
        page_title="🆓 완전 무료 한국어 AI", page_icon="💰", layout="wide"
    )

    # --- 상태 초기화 ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 어떤 이야기를 만들어볼까요?"}
        ]
    if "last_response" not in st.session_state:
        st.session_state.last_response = ""
    
    # --- 헤더 ---
    _ = st.title("🆓 완전 무료 한국어 창작 AI")
    _ = st.markdown("**OpenAI API 없이도 작동하는 로컬 AI** 💪")

    # --- Ollama 설치 확인 ---
    if not check_ollama_installed():
        install_ollama_guide()
        return

    # 설치된 모델 확인
    installed_models = get_available_models()

    # --- 사이드바 ---
    with st.sidebar:
        _ = st.header("⚙️ 설정")

        # 모델 선택
        if installed_models:
            selected_model = st.selectbox(
                "모델 선택",
                installed_models,
                help="사용 가능한 모델 중에서 선택하세요.",
                index=0
                if "solar:10.7b-instruct-v1-q4_K_M" not in installed_models
                else installed_models.index("solar:10.7b-instruct-v1-q4_K_M"),
            )
        else:
            _ = st.warning("설치된 모델이 없습니다! 먼저 모델을 다운로드해주세요.")
            selected_model = None

        # 모델 다운로드 섹션
        _ = st.subheader("📥 모델 다운로드")

        for model_id, info in AVAILABLE_MODELS.items():
            with st.expander(f"📦 {info['name']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    _ = st.write(f"**크기**: {info['size']}")
                    _ = st.write(f"**품질**: {info['quality']}")
                    _ = st.write(f"**속도**: {info['speed']}")

                with col2:
                    if model_id in installed_models:
                        _ = st.success("✅ 설치됨")
                    else:
                        if st.button("다운로드", key=f"download_{model_id}"):
                            with st.spinner(f"{info['name']} 다운로드 중..."):
                                if download_model(model_id):
                                    st.success("다운로드 완료!")
                                    st.rerun()
                                else:
                                    st.error("다운로드 실패")

        # 고급 설정
        _ = st.subheader("🎛️ 생성 설정")
        temperature = st.slider("창의성 (Temperature)", 0.1, 1.0, 0.8, 0.05)

        _ = st.info(
            "**창의성**: 값이 높을수록 다양하고 예측 불가능한 이야기를, 낮을수록 안정적이고 일관된 이야기를 생성합니다."
        )

        # 비용 비교
        _ = st.subheader("💰 비용 비교")
        _ = st.write("**로컬 AI**: $0 (전기료만)")
        _ = st.write("**OpenAI API**: 월 $5-50")
        _ = st.write("**절약액**: 월 $60-600")

    # --- 메인 콘텐츠 ---
    if not selected_model:
        _ = st.warning("사이드바에서 사용할 모델을 선택하거나 다운로드해주세요!")
        return

    # 이전 대화 내용 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("여기에 창작 요청을 입력하세요..."):
        # 사용자 메시지 추가 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답 생성 및 표시 (스트리밍)
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            for chunk in generate_with_ollama(prompt, selected_model, temperature):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        
        # AI 메시지 저장
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.last_response = full_response


if __name__ == "__main__":
    main()
