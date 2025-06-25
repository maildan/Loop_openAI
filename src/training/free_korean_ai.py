import streamlit as st
import requests
import json
import subprocess
import os
from datetime import datetime

# 로컬 모델 설정
AVAILABLE_MODELS = {
    "solar:10.7b-instruct-v1-q4_K_M": {
        "name": "SOLAR 10.7B (한국어 특화)",
        "size": "6.4GB",
        "quality": "⭐⭐⭐⭐⭐",
        "speed": "빠름"
    },
    "qwen2.5:7b-instruct-q4_K_M": {
        "name": "Qwen2.5 7B (다국어)",
        "size": "4.4GB", 
        "quality": "⭐⭐⭐⭐",
        "speed": "매우 빠름"
    },
    "llama3.2:3b-instruct-q4_K_M": {
        "name": "Llama 3.2 3B (경량)",
        "size": "1.9GB",
        "quality": "⭐⭐⭐",
        "speed": "초고속"
    }
}

def check_ollama_installed():
    """Ollama 설치 확인"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ollama_guide():
    """Ollama 설치 가이드"""
    st.error("🚨 Ollama가 설치되지 않았습니다!")
    
    st.markdown("""
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
    """)
    
    if st.button("🔄 새로고침 (설치 후 클릭)"):
        st.rerun()

def get_available_models():
    """설치된 모델 목록 가져오기"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # 헤더 제외
            models = []
            for line in lines:
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            return models
        return []
    except:
        return []

def download_model(model_name):
    """모델 다운로드"""
    try:
        process = subprocess.Popen(
            ['ollama', 'pull', model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 실시간 진행상황 표시
        progress_placeholder = st.empty()
        
        while True:
            if process.stdout is not None:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    progress_placeholder.text(f"다운로드 중: {output.strip()}")
            else:
                break
        
        return process.returncode == 0
    except:
        return False

def generate_with_ollama(prompt, model="solar:10.7b-instruct-v1-q4_K_M", temperature=0.8):
    """Ollama로 한국어 생성"""
    try:
        korean_prompt = f"""당신은 한국어 창작 전문가입니다.

요청: {prompt}

자연스럽고 창의적인 한국어로 창작해주세요. 한국적 정서와 문화를 반영하여 흥미로운 이야기를 만들어주세요."""

        response = requests.post('http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': korean_prompt,
                'stream': False,
                'options': {
                    'temperature': temperature,
                    'top_p': 0.9,
                    'max_tokens': 1000
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return json.loads(response.text)['response']
        else:
            return f"오류가 발생했습니다: HTTP {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Ollama 서버에 연결할 수 없습니다. 'ollama serve' 명령으로 서버를 시작해주세요."
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

def main():
    st.set_page_config(
        page_title="🆓 완전 무료 한국어 AI",
        page_icon="💰",
        layout="wide"
    )
    
    # 헤더
    st.title("🆓 완전 무료 한국어 창작 AI")
    st.markdown("**OpenAI API 없이도 작동하는 로컬 AI** 💪")
    
    # Ollama 설치 확인
    if not check_ollama_installed():
        install_ollama_guide()
        return
    
    # 설치된 모델 확인
    installed_models = get_available_models()
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 모델 선택
        if installed_models:
            selected_model = st.selectbox(
                "모델 선택",
                installed_models,
                help="설치된 모델 중에서 선택하세요"
            )
        else:
            st.warning("설치된 모델이 없습니다!")
            selected_model = None
        
        # 모델 다운로드 섹션
        st.subheader("📥 모델 다운로드")
        
        for model_id, info in AVAILABLE_MODELS.items():
            with st.expander(f"📦 {info['name']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**크기**: {info['size']}")
                    st.write(f"**품질**: {info['quality']}")
                    st.write(f"**속도**: {info['speed']}")
                
                with col2:
                    if model_id in installed_models:
                        st.success("✅ 설치됨")
                    else:
                        if st.button(f"다운로드", key=f"download_{model_id}"):
                            with st.spinner(f"{info['name']} 다운로드 중..."):
                                if download_model(model_id):
                                    st.success("다운로드 완료!")
                                    st.rerun()
                                else:
                                    st.error("다운로드 실패")
        
        # 고급 설정
        st.subheader("🎛️ 생성 설정")
        temperature = st.slider("창의성", 0.1, 1.0, 0.8, 0.1)
        
        # 비용 비교
        st.subheader("💰 비용 비교")
        st.write("**로컬 AI**: $0 (전기료만)")
        st.write("**OpenAI API**: 월 $5-50")
        st.write("**절약액**: 월 $60-600")
    
    # 메인 콘텐츠
    if not installed_models:
        st.warning("먼저 모델을 다운로드해주세요!")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 창작 요청")
        
        # 장르별 예시
        genre_examples = {
            "판타지": "마법사 학교에 입학한 평범한 학생의 모험",
            "로맨스": "카페에서 만난 두 사람의 운명적 만남",
            "SF": "AI가 감정을 가지게 되면서 벌어지는 일",
            "미스터리": "사라진 친구를 찾는 대학생의 추리",
            "일상": "평범한 회사원의 특별한 하루"
        }
        
        # 장르 선택
        selected_genre = st.selectbox("장르 선택", list(genre_examples.keys()))
        example_text = genre_examples[selected_genre]
        
        # 프롬프트 입력
        prompt = st.text_area(
            "창작 요청을 입력하세요",
            height=150,
            placeholder=f"예시: {example_text}"
        )
        
        # 생성 버튼
        if st.button("✨ 무료로 창작하기", type="primary"):
            if prompt.strip() and selected_model is not None:
                with st.spinner("창작 중... (로컬에서 처리 중) ⏳"):
                    result = generate_with_ollama(prompt, selected_model, temperature)
                    st.session_state.result = result
                    st.session_state.prompt = prompt
                    st.session_state.model = selected_model
                    st.session_state.timestamp = datetime.now()
            else:
                if not prompt.strip():
                    st.warning("창작 요청을 입력해주세요!")
                else:
                    st.warning("모델을 선택해주세요!")
    
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
                st.write(f"**모델**: {st.session_state.model.split(':')[0]}")
            with col_info2:
                st.write(f"**생성 시간**: {st.session_state.timestamp.strftime('%H:%M:%S')}")
            with col_info3:
                word_count = len(st.session_state.result.replace(' ', ''))
                st.write(f"**글자 수**: {word_count:,}자")
            
            # 액션 버튼들
            st.markdown("---")
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                st.download_button(
                    label="💾 다운로드",
                    data=st.session_state.result,
                    file_name=f"창작물_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
            with col_btn2:
                if st.button("➕ 이어쓰기"):
                    if selected_model is not None:
                        continue_prompt = f"다음 내용을 이어서 써주세요:\n\n{st.session_state.result}\n\n계속:"
                        with st.spinner("이어쓰기 중..."):
                            continued = generate_with_ollama(continue_prompt, selected_model, temperature)
                            st.session_state.result += "\n\n" + continued
                            st.rerun()
                    else:
                        st.warning("모델을 선택해주세요!")
            
            with col_btn3:
                if st.button("🔄 다시 생성"):
                    if selected_model is not None:
                        with st.spinner("다시 생성 중..."):
                            new_result = generate_with_ollama(st.session_state.prompt, selected_model, temperature)
                            st.session_state.result = new_result
                            st.rerun()
                    else:
                        st.warning("모델을 선택해주세요!")
        
        else:
            st.info("왼쪽에서 창작 요청을 입력하고 '무료로 창작하기' 버튼을 눌러주세요!")
    
    # 성능 비교
    st.markdown("---")
    st.subheader("📊 성능 비교")
    
    comparison_data = {
        "특징": ["비용", "속도", "프라이버시", "오프라인", "품질"],
        "로컬 AI (무료)": ["$0", "빠름", "100% 안전", "가능", "⭐⭐⭐⭐"],
        "OpenAI API": ["월 $5-50", "매우 빠름", "데이터 전송", "불가능", "⭐⭐⭐⭐⭐"]
    }
    
    st.table(comparison_data)
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🆓 <strong>완전 무료 한국어 AI</strong> 🆓</p>
        <p>OpenAI API 없이도 충분히 좋은 품질!</p>
        <p>💰 <strong>월 $60-600 절약</strong> 💰</p>
        <p><em>"무료가 최고다!" - 모든 개발자</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 