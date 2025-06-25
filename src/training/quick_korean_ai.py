import openai
import streamlit as st
import os
import asyncio
import time
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

# OpenAI API 키 설정
api_key = os.getenv("OPEN_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except:
        pass
        
if not api_key:
    st.error("❌ API 키가 설정되지 않았습니다! 환경변수 OPEN_API_KEY 또는 OPENAI_API_KEY를 설정해주세요.")
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

다음 요청에 따라 창작해주세요:"""
}

def generate_korean_content_with_progress(prompt, genre="소설", temperature=0.8, max_tokens=1000):
    """진행상황 표시와 함께 한국어 창작 생성"""
    
    # 진행상황 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🤖 AI 모델 준비 중...")
        progress_bar.progress(10)
        time.sleep(0.5)
        
        system_prompt = GENRE_PROMPTS.get(genre, KOREAN_CREATIVE_PROMPT)
        
        status_text.text("✍️ 창작 시작...")
        progress_bar.progress(30)
        time.sleep(0.5)
        
        # OpenAI API 호출
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            stream=True  # 스트리밍 모드로 타임아웃 방지
        )
        
        status_text.text("📝 텍스트 생성 중...")
        progress_bar.progress(60)
        
        # 스트리밍 응답 처리
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
        
        progress_bar.progress(90)
        status_text.text("✅ 완료!")
        time.sleep(0.5)
        
        progress_bar.progress(100)
        status_text.text("🎉 창작 완료!")
        
        # UI 정리
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return full_response
    
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        return f"오류가 발생했습니다: {str(e)}"

def generate_korean_content(prompt, genre="소설", temperature=0.8, max_tokens=1000):
    """기존 함수 (백업용)"""
    try:
        system_prompt = GENRE_PROMPTS.get(genre, KOREAN_CREATIVE_PROMPT)
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

def main():
    st.set_page_config(
        page_title="🇰🇷 한국어 창작 AI",
        page_icon="✍️",
        layout="wide"
    )
    
    # 헤더
    st.title("🇰🇷 한국어 창작 AI")
    st.markdown("**30분 만에 만든 실용적인 한국어 창작 도구** 🚀")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 장르 선택
        genre = st.selectbox(
            "장르 선택",
            ["판타지", "로맨스", "SF", "미스터리", "드라마"],
            index=0
        )
        
        # 고급 설정
        st.subheader("고급 설정")
        temperature = st.slider("창의성 (Temperature)", 0.1, 1.0, 0.8, 0.1)
        max_tokens = st.slider("최대 길이", 200, 2000, 1000, 100)
        
        # 비용 계산
        st.subheader("💰 예상 비용")
        cost_per_request = 0.0005  # 실제 계산된 비용
        st.write(f"요청당: ${cost_per_request:.4f}")
        st.write(f"월 1000회: ${cost_per_request * 1000:.2f}")
    
    # 메인 콘텐츠
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 창작 요청")
        
        # 예시 프롬프트
        examples = {
            "판타지": "마법사 학교에 입학한 평범한 학생이 숨겨진 능력을 발견하는 이야기",
            "로맨스": "카페에서 우연히 만난 두 사람의 운명적인 사랑 이야기",
            "SF": "AI가 인간의 감정을 이해하게 되면서 벌어지는 일",
            "미스터리": "연쇄 실종 사건을 수사하는 형사의 이야기",
            "드라마": "가족의 비밀이 밝혀지면서 벌어지는 갈등과 화해"
        }
        
        example_prompt = examples.get(genre, "")
        
        # 프롬프트 입력
        prompt = st.text_area(
            "창작 요청을 입력하세요",
            value="",
            height=150,
            placeholder=f"예시: {example_prompt}"
        )
        
        # 생성 버튼
        if st.button("✨ 창작하기", type="primary"):
            if prompt.strip():
                # 진행상황과 함께 생성
                result = generate_korean_content_with_progress(prompt, genre, temperature, max_tokens)
                raw_result = str(result) if result is not None else ""
                st.session_state.result = raw_result
                st.session_state.prompt = prompt
                st.session_state.genre = genre
                st.session_state.timestamp = datetime.now()
            else:
                st.warning("창작 요청을 입력해주세요!")
    
    with col2:
        st.subheader("📖 창작 결과")
        
        if 'result' in st.session_state:
            # 결과 표시
            st.markdown("### 생성된 작품")
            st.write(st.session_state.result)
            
            # 메타 정보
            st.markdown("---")
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.write(f"**장르**: {st.session_state.genre}")
            with col_info2:
                st.write(f"**생성 시간**: {st.session_state.timestamp.strftime('%H:%M:%S')}")
            with col_info3:
                word_count = len(str(st.session_state.result or "").replace(' ', ''))
                st.write(f"**글자 수**: {word_count:,}자")
            
            # 액션 버튼들
            st.markdown("---")
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("📋 복사하기"):
                    st.write("텍스트를 선택해서 복사하세요!")
            
            with col_btn2:
                if st.button("💾 다운로드"):
                    filename = f"{st.session_state.genre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    st.download_button(
                        label="TXT 파일 다운로드",
                        data=str(st.session_state.result or ""),
                        file_name=filename,
                        mime="text/plain"
                    )
            
            with col_btn3:
                if st.button("➕ 이어쓰기"):
                    continue_prompt = f"다음 내용을 이어서 써주세요:\n\n{st.session_state.result}\n\n계속:"
                    with st.spinner("이어쓰기 중..."):
                        cont_raw = generate_korean_content(continue_prompt, st.session_state.genre, temperature, max_tokens)
                        continued = str(cont_raw) if cont_raw is not None else ""
                        st.session_state.result = (st.session_state.result or "") + "\n\n" + continued
                        st.rerun()
        
        else:
            st.info("왼쪽에서 창작 요청을 입력하고 '창작하기' 버튼을 눌러주세요!")
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🔥 <strong>30분 만에 만든 현실적인 한국어 AI</strong> 🔥</p>
        <p>과엔지니어링 없이 바로 써먹을 수 있는 실용적 도구</p>
        <p><em>"Done is better than perfect" - Mark Zuckerberg</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 