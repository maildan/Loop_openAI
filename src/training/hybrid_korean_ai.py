import streamlit as st
import requests
import json
import subprocess
import os
import time
from datetime import datetime

# OpenAI 가져오기 (선택적)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class HybridKoreanAI:
    def __init__(self):
        self.openai_key = os.getenv("OPEN_API_KEY") or os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
        self.use_openai = bool(self.openai_key) and OPENAI_AVAILABLE
        
        if self.use_openai:
            openai.api_key = self.openai_key
    
    def check_ollama_available(self):
        """Ollama 사용 가능 여부 확인"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self):
        """사용 가능한 모델 목록"""
        models = {}
        
        # OpenAI 모델
        if self.use_openai:
            models.update({
                "gpt-4o-mini": {
                    "name": "GPT-4o Mini (OpenAI)",
                    "type": "api",
                    "cost": "월 $5-10",
                    "quality": "⭐⭐⭐⭐⭐",
                    "speed": "매우 빠름"
                },
                "gpt-3.5-turbo": {
                    "name": "GPT-3.5 Turbo (OpenAI)",
                    "type": "api", 
                    "cost": "월 $3-8",
                    "quality": "⭐⭐⭐⭐",
                    "speed": "초고속"
                }
            })
        
        # 로컬 모델 (Ollama)
        if self.check_ollama_available():
            try:
                response = requests.get('http://localhost:11434/api/tags')
                if response.status_code == 200:
                    ollama_models = response.json().get('models', [])
                    for model in ollama_models:
                        model_name = model['name']
                        models[f"local_{model_name}"] = {
                            "name": f"{model_name} (로컬)",
                            "type": "local",
                            "cost": "무료",
                            "quality": "⭐⭐⭐⭐" if "solar" in model_name else "⭐⭐⭐",
                            "speed": "빠름"
                        }
            except:
                pass
        
        return models
    
    def generate_with_openai(self, prompt, model="gpt-4o-mini", temperature=0.8, progress_callback=None):
        """OpenAI API로 생성 (진행상황 표시 포함)"""
        try:
            if progress_callback:
                progress_callback(10, "🤖 OpenAI API 준비 중...")
            
            system_prompt = """당신은 한국어 창작 전문가입니다.

특징:
- 자연스러운 한국어 사용
- 창의적이고 흥미로운 스토리
- 적절한 높임법과 문체
- 한국적 정서와 문화 반영

사용자의 요청에 따라 소설, 시나리오, 에세이 등을 창작해주세요."""

            if progress_callback:
                progress_callback(30, "✍️ 창작 시작...")

            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=temperature,
                top_p=0.9,
                stream=True  # 스트리밍으로 타임아웃 방지
            )
            
            if progress_callback:
                progress_callback(60, "📝 텍스트 생성 중...")
            
            # 스트리밍 응답 처리
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
            
            if progress_callback:
                progress_callback(100, "🎉 완료!")
            
            return full_response
        except Exception as e:
            return f"OpenAI API 오류: {str(e)}"
    
    def generate_with_ollama(self, prompt, model, temperature=0.8):
        """Ollama로 생성"""
        try:
            # local_ 접두사 제거
            actual_model = model.replace("local_", "")
            
            korean_prompt = f"""당신은 한국어 창작 전문가입니다.

요청: {prompt}

자연스럽고 창의적인 한국어로 창작해주세요. 한국적 정서와 문화를 반영하여 흥미로운 이야기를 만들어주세요."""

            response = requests.post('http://localhost:11434/api/generate',
                json={
                    'model': actual_model,
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
                return f"Ollama 오류: HTTP {response.status_code}"
                
        except Exception as e:
            return f"로컬 모델 오류: {str(e)}"
    
    def generate(self, prompt, model_id, temperature=0.8):
        """통합 생성 함수"""
        models = self.get_available_models()
        
        if model_id not in models:
            return "선택된 모델을 찾을 수 없습니다."
        
        model_info = models[model_id]
        
        if model_info['type'] == 'api':
            return self.generate_with_openai(prompt, model_id, temperature)
        elif model_info['type'] == 'local':
            return self.generate_with_ollama(prompt, model_id, temperature)
        else:
            return "지원하지 않는 모델 타입입니다."

def setup_guide():
    """설정 가이드"""
    st.markdown("""
    ## 🔧 설정 가이드
    
    ### Option 1: OpenAI API 사용 (고품질)
    1. OpenAI API 키를 환경변수에 설정:
    ```bash
    export OPENAI_API_KEY="sk-your-key-here"
    ```
    2. 또는 Streamlit secrets에 추가
    3. **비용**: 월 $5-10 (매우 저렴)
    4. **품질**: ⭐⭐⭐⭐⭐
    
    ### Option 2: 로컬 모델 사용 (무료)
    1. Ollama 설치:
    ```bash
    # macOS
    brew install ollama
    
    # Linux
    curl -fsSL https://ollama.com/install.sh | sh
    ```
    2. 모델 다운로드:
    ```bash
    ollama pull solar:10.7b-instruct-v1-q4_K_M
    ```
    3. 서버 시작:
    ```bash
    ollama serve
    ```
    4. **비용**: 무료 (전기료만)
    5. **품질**: ⭐⭐⭐⭐
    
    ### 🎯 권장사항
    - **빠른 시작**: OpenAI API (30분 설정)
    - **장기 사용**: 로컬 모델 (무료)
    - **최고 품질**: 하이브리드 (둘 다 사용)
    """)

def main():
    st.set_page_config(
        page_title="🔀 하이브리드 한국어 AI",
        page_icon="⚡",
        layout="wide"
    )
    
    # 헤더
    st.title("🔀 하이브리드 한국어 창작 AI")
    st.markdown("**OpenAI API + 로컬 모델을 자동으로 선택하는 스마트 AI** ⚡")
    
    # AI 초기화
    ai = HybridKoreanAI()
    available_models = ai.get_available_models()
    
    # 설정 상태 표시
    col_status1, col_status2, col_status3 = st.columns(3)
    
    with col_status1:
        if ai.use_openai:
            st.success("✅ OpenAI API 연결됨")
        else:
            st.warning("⚠️ OpenAI API 없음")
    
    with col_status2:
        if ai.check_ollama_available():
            st.success("✅ 로컬 모델 사용 가능")
        else:
            st.warning("⚠️ 로컬 모델 없음")
    
    with col_status3:
        total_models = len(available_models)
        if total_models > 0:
            st.info(f"📊 사용 가능한 모델: {total_models}개")
        else:
            st.error("❌ 사용 가능한 모델 없음")
    
    # 모델이 없으면 설정 가이드 표시
    if not available_models:
        setup_guide()
        return
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 모델 선택
        st.subheader("🤖 모델 선택")
        
        # 모델을 타입별로 그룹화
        api_models = {k: v for k, v in available_models.items() if v['type'] == 'api'}
        local_models = {k: v for k, v in available_models.items() if v['type'] == 'local'}
        
        model_options = []
        if api_models:
            model_options.append("--- OpenAI API 모델 ---")
            model_options.extend(list(api_models.keys()))
        
        if local_models:
            model_options.append("--- 로컬 모델 ---")
            model_options.extend(list(local_models.keys()))
        
        # 구분선 제거한 실제 모델만 필터링
        actual_models = [m for m in model_options if not m.startswith("---")]
        
        selected_model = st.selectbox(
            "모델 선택",
            actual_models,
            format_func=lambda x: available_models[x]['name'] if x in available_models else x
        )
        
        # 선택된 모델 정보 표시
        if selected_model in available_models:
            model_info = available_models[selected_model]
            st.info(f"""
            **선택된 모델**: {model_info['name']}
            **비용**: {model_info['cost']}
            **품질**: {model_info['quality']}
            **속도**: {model_info['speed']}
            """)
        
        # 생성 설정
        st.subheader("🎛️ 생성 설정")
        temperature = st.slider("창의성", 0.1, 1.0, 0.8, 0.1)
        
        # 비용 비교
        st.subheader("💰 비용 비교")
        if ai.use_openai:
            st.success("OpenAI API: 월 $5-10")
        else:
            st.info("OpenAI API: 설정 안됨")
        
        if ai.check_ollama_available():
            st.success("로컬 모델: 무료")
        else:
            st.info("로컬 모델: 설정 안됨")
        
        # 추천 설정
        st.subheader("💡 추천 설정")
        if st.button("🚀 빠른 시작 (API)"):
            if api_models:
                selected_model = list(api_models.keys())[0]
                st.rerun()
        
        if st.button("💰 무료 사용 (로컬)"):
            if local_models:
                selected_model = list(local_models.keys())[0]
                st.rerun()
    
    # 메인 콘텐츠
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 창작 요청")
        
        # 장르별 예시
        genre_examples = {
            "판타지 소설": "마법 학교에 입학한 평범한 학생이 숨겨진 능력을 발견하는 이야기를 써주세요.",
            "로맨스 소설": "카페에서 우연히 만난 두 사람이 운명적인 사랑에 빠지는 이야기를 써주세요.",
            "SF 소설": "AI가 인간의 감정을 이해하게 되면서 벌어지는 일을 그린 이야기를 써주세요.",
            "미스터리": "대학교에서 일어난 연쇄 실종 사건을 수사하는 형사의 이야기를 써주세요.",
            "일상 드라마": "평범한 회사원이 겪는 특별한 하루를 그린 감동적인 이야기를 써주세요."
        }
        
        # 장르 선택
        selected_genre = st.selectbox("장르 선택", list(genre_examples.keys()))
        example_text = genre_examples[selected_genre]
        
        # 프롬프트 입력
        prompt = st.text_area(
            "창작 요청을 입력하세요",
            height=150,
            placeholder=example_text
        )
        
        # 예시 버튼들
        st.markdown("**빠른 예시:**")
        col_ex1, col_ex2 = st.columns(2)
        
        with col_ex1:
            if st.button("📖 예시 사용"):
                prompt = example_text
                st.rerun()
        
        with col_ex2:
            if st.button("🎲 랜덤 예시"):
                import random
                random_genre = random.choice(list(genre_examples.keys()))
                prompt = genre_examples[random_genre]
                st.rerun()
        
        # 생성 버튼
        if st.button("✨ 창작하기", type="primary"):
            if prompt.strip() and selected_model:
                model_info = available_models[selected_model]
                cost_info = f"({model_info['cost']})" if model_info['cost'] != "무료" else "(무료)"
                
                with st.spinner(f"창작 중... {cost_info} ⏳"):
                    raw_result = ai.generate(prompt, selected_model, temperature)
                    result = str(raw_result) if raw_result is not None else ""
                    st.session_state.result = result
                    st.session_state.prompt = prompt
                    st.session_state.model = selected_model
                    st.session_state.model_info = model_info
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
                st.write(f"**모델**: {st.session_state.model_info['name']}")
            with col_info2:
                st.write(f"**비용**: {st.session_state.model_info['cost']}")
            with col_info3:
                word_count = len(str(st.session_state.result or "").replace(' ', ''))
                st.write(f"**글자 수**: {word_count:,}자")
            
            # 품질 평가
            st.markdown("---")
            st.write("**이 결과가 어떠셨나요?**")
            col_rating1, col_rating2, col_rating3, col_rating4 = st.columns(4)
            
            with col_rating1:
                if st.button("😍 훌륭함"):
                    st.success("피드백 감사합니다!")
            with col_rating2:
                if st.button("👍 좋음"):
                    st.success("피드백 감사합니다!")
            with col_rating3:
                if st.button("👌 보통"):
                    st.info("더 나은 결과를 위해 노력하겠습니다!")
            with col_rating4:
                if st.button("👎 아쉬움"):
                    st.info("다른 모델이나 설정을 시도해보세요!")
            
            # 액션 버튼들
            st.markdown("---")
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                st.download_button(
                    label="💾 다운로드",
                    data=str(st.session_state.result or ""),
                    file_name=f"창작물_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
            with col_btn2:
                if st.button("➕ 이어쓰기"):
                    if st.session_state.model is not None:
                        continue_prompt = f"다음 내용을 이어서 써주세요:\n\n{st.session_state.result}\n\n계속:"
                        with st.spinner("이어쓰기 중..."):
                            cont_raw = ai.generate(continue_prompt, st.session_state.model, temperature)
                            continued = str(cont_raw) if cont_raw is not None else ""
                            st.session_state.result = (st.session_state.result or "") + "\n\n" + continued
                            st.rerun()
                    else:
                        st.warning("모델을 선택해주세요!")
            
            with col_btn3:
                if st.button("🔄 다시 생성"):
                    with st.spinner("다시 생성 중..."):
                        new_raw = ai.generate(st.session_state.prompt, st.session_state.model, temperature)
                        new_result = str(new_raw) if new_raw is not None else ""
                        st.session_state.result = new_result
                        st.rerun()
        
        else:
            st.info("왼쪽에서 창작 요청을 입력하고 '창작하기' 버튼을 눌러주세요!")
    
    # 모델 비교 섹션
    if len(available_models) > 1:
        st.markdown("---")
        st.subheader("📊 모델 비교")
        
        comparison_data = []
        for model_id, info in available_models.items():
            comparison_data.append({
                "모델": info['name'],
                "타입": "API" if info['type'] == 'api' else "로컬",
                "비용": info['cost'],
                "품질": info['quality'],
                "속도": info['speed']
            })
        
        st.table(comparison_data)
    
    # 팁 섹션
    st.markdown("---")
    st.subheader("💡 사용 팁")
    
    col_tip1, col_tip2, col_tip3 = st.columns(3)
    
    with col_tip1:
        st.markdown("""
        **💰 비용 절약**
        - 로컬 모델로 초안 작성
        - API 모델로 최종 다듬기
        - 간단한 요청은 로컬 사용
        """)
    
    with col_tip2:
        st.markdown("""
        **⚡ 속도 최적화**
        - 짧은 프롬프트 사용
        - 구체적인 요청하기
        - 적절한 온도 설정
        """)
    
    with col_tip3:
        st.markdown("""
        **🎯 품질 향상**
        - 구체적인 장르 지정
        - 원하는 분위기 명시
        - 예시 포함해서 요청
        """)
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🔀 <strong>하이브리드 한국어 AI</strong> 🔀</p>
        <p>최고의 품질과 최적의 비용을 동시에!</p>
        <p><em>"선택의 자유가 진짜 자유다!" - 스마트한 개발자</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 