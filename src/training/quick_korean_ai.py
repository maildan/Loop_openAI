import openai
import streamlit as st
import os
import time
from datetime import datetime
from typing import TypedDict, Literal, List
from openai.types.chat import ChatCompletionMessageParam

# --- Type Definitions ---
class ChatMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str

# SessionState TypedDict is removed to let Pyright handle SessionStateProxy directly

# --- OpenAI API Key Setup ---
api_key = os.getenv("OPEN_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass

if not api_key:
    _ = st.error(
        "❌ API 키가 설정되지 않았습니다! 환경변수 OPEN_API_KEY 또는 OPENAI_API_KEY를 설정해주세요."
    )
    st.stop()

openai.api_key = api_key

# 한국어 창작 전문 시스템 프롬프트
KOREAN_CREATIVE_PROMPT = """당신은 한국어 창작 전문가입니다.

특징:
- 자연스러운 한국어 사용
- 창의적이고 흥미로운 스토리
- 적절한 높임법과 문체
- 한국적 정서와 문화 반영

사용자의 요청에 따라 소설, 시나리오, 에세이 등을 창작해주세요."""

# 장르별 특화 프롬프트
GENRE_PROMPTS = {
    "판타지": """당신은 한국 판타지 소설 작가입니다.
    
특징:
- 한국적 정서와 서구 판타지의 조화
- 전통 신화 요소 활용
- 현대적 갈등 구조
- 감정적 몰입도 높은 문체

다음 요청에 따라 창작해주세요:""",
    "로맨스": """당신은 한국 로맨스 소설 전문가입니다.
    
특징:
- 섬세한 감정 묘사
- 한국적 연애 문화 반영
- 현실적이면서도 로맨틱
- 독자의 감정 이입 유도

다음 요청에 따라 창작해주세요:""",
    "SF": """당신은 한국 SF 소설 작가입니다.
    
특징:
- 과학적 상상력과 한국적 현실의 결합
- 사회 비판적 요소 포함
- 미래 기술과 인간성의 갈등
- 논리적이면서도 감성적

다음 요청에 따라 창작해주세요:""",
    "미스터리": """당신은 한국 미스터리 소설 작가입니다.
    
특징:
- 치밀한 추리와 반전
- 한국 사회의 현실 반영
- 긴장감 넘치는 전개
- 독자의 호기심 자극

다음 요청에 따라 창작해주세요:""",
    "드라마": """당신은 한국 드라마 작가입니다.
    
특징:
- 일상적이면서도 감동적인 스토리
- 한국 가족 문화 반영
- 현실적인 갈등과 해결
- 따뜻한 인간미

다음 요청에 따라 창작해주세요:""",
}


def generate_korean_content_with_progress(
    prompt: str, genre: str = "소설", temperature: float = 0.8, max_tokens: int = 1000
) -> str:
    """진행상황 표시와 함께 한국어 창작 생성"""
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        _ = status_text.text("🤖 AI 모델 준비 중...")
        progress_bar.progress(10)
        time.sleep(0.5)

        system_prompt = GENRE_PROMPTS.get(genre, KOREAN_CREATIVE_PROMPT)

        _ = status_text.text("✍️ 창작 시작...")
        progress_bar.progress(30)
        time.sleep(0.5)

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            stream=True,
        )

        _ = status_text.text("📝 텍스트 생성 중...")
        progress_bar.progress(60)

        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content

        progress_bar.progress(90)
        _ = status_text.text("✅ 완료!")
        time.sleep(0.5)

        progress_bar.progress(100)
        _ = status_text.text("🎉 창작 완료!")

        time.sleep(1)
        progress_bar.empty()
        status_text.empty()

        return full_response

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"오류가 발생했습니다: {str(e)}")
        return ""


def generate_korean_content(
    prompt: str, genre: str = "소설", temperature: float = 0.8, max_tokens: int = 1000
) -> str:
    """기존 함수 (백업용)"""
    try:
        system_prompt = GENRE_PROMPTS.get(genre, KOREAN_CREATIVE_PROMPT)

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
        )
        content = response.choices[0].message.content
        return content if content else ""

    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
        return ""


def main() -> None:
    _ = st.set_page_config(page_title="🇰🇷 한국어 창작 AI", page_icon="✍️", layout="wide")

    _ = st.title("🇰🇷 한국어 창작 AI")
    _ = st.markdown("**30분 만에 만든 실용적인 한국어 창작 도구** 🚀")

    with st.sidebar:
        _ = st.header("⚙️ 설정")
        genre_options = ["판타지", "로맨스", "SF", "미스터리", "드라마"]
        genre = st.selectbox("장르 선택", genre_options, index=0)
        selected_genre = str(genre)

        _ = st.subheader("고급 설정")
        temperature = st.slider("창의성 (Temperature)", 0.1, 1.0, 0.8, 0.1)
        max_tokens = st.slider("최대 길이", 200, 2000, 1000, 100)

        _ = st.subheader("💰 예상 비용")
        cost_per_request = 0.0005
        _ = st.write(f"요청당: ${cost_per_request:.4f}")
        _ = st.write(f"월 1000회: ${cost_per_request * 1000:.2f}")

    col1, col2 = st.columns([1, 1])

    with col1:
        _ = st.subheader("📝 창작 요청")
        examples = {
            "판타지": "마법사 학교에 입학한 평범한 학생이 숨겨진 능력을 발견하는 이야기",
            "로맨스": "카페에서 우연히 만난 두 사람의 운명적인 사랑 이야기",
            "SF": "AI가 인간의 감정을 이해하게 되면서 벌어지는 일",
            "미스터리": "연쇄 실종 사건을 수사하는 형사의 이야기",
            "드라마": "가족의 비밀이 밝혀지면서 벌어지는 갈등과 화해",
        }
        example_prompt = examples.get(selected_genre, "")

        prompt_input = st.text_area(
            "창작 요청을 입력하세요",
            value="",
            height=150,
            placeholder=f"예시: {example_prompt}",
        )
        prompt = str(prompt_input)

        if st.button("✨ 창작하기", type="primary"):
            if prompt.strip():
                result = generate_korean_content_with_progress(
                    prompt, selected_genre, float(temperature), int(max_tokens)
                )
                st.session_state.result = result
                st.session_state.prompt = prompt
                st.session_state.genre = selected_genre
                st.session_state.timestamp = datetime.now()
            else:
                _ = st.warning("창작 요청을 입력해주세요!")

    with col2:
        _ = st.subheader("📖 창작 결과")
        if "result" in st.session_state:
            _ = st.markdown("### 생성된 작품")
            _ = st.write(st.session_state.result)
            _ = st.markdown("---")
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                _ = st.write(f"**장르**: {st.session_state.genre}")
            with col_info2:
                if "timestamp" in st.session_state and st.session_state.timestamp:
                    _ = st.write(f"**시간**: {st.session_state.timestamp.strftime('%Y-%m-%d %H:%M')}")
            with col_info3:
                def clear_result():
                    if "result" in st.session_state:
                        del st.session_state.result
                    if "prompt" in st.session_state:
                        del st.session_state.prompt
                    if "genre" in st.session_state:
                        del st.session_state.genre
                    if "timestamp" in st.session_state:
                        del st.session_state.timestamp

                _ = st.button("결과 지우기", on_click=clear_result)


# --- 챗봇 AI ---
def chatbot_main() -> None:
    _ = st.header("🤖 한국어 챗봇 AI")

    if "messages" not in st.session_state:
        initial_messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": "당신은 친절한 한국어 챗봇입니다."}
        ]
        st.session_state.messages = initial_messages

    for message in st.session_state.messages:
        role = message.get("role")
        content = message.get("content")
        if role and isinstance(content, str):
            with st.chat_message(role):
                _ = st.markdown(content)

    user_input_raw = st.chat_input("무엇이든 물어보세요...")
    if user_input_raw:
        user_input = str(user_input_raw)
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            _ = st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages,
                    stream=True,
                )
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        _ = message_placeholder.markdown(full_response + "▌")
                _ = message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"오류 발생: {e}"
                _ = message_placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    main()
    _ = st.divider()
    chatbot_main()
