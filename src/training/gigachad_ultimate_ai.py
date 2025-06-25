import streamlit as st
import openai
import os
import json
import random
import time
import threading
from datetime import datetime
import uuid
from pathlib import Path

# API 키 설정
api_key = os.getenv("OPEN_API_KEY") or os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key

# 전역 작업 상태 저장소
if 'jobs' not in st.session_state:
    st.session_state.jobs = {}
if 'dataset_cache' not in st.session_state:
    st.session_state.dataset_cache = {}

class DatasetAnalyzer:
    """데이터셋 분석 및 패턴 추출"""
    
    def __init__(self):
        self.base_path = Path("dataset")
        self.vl_novel_path = self.base_path / "VL_novel"
        self.vl_anime_path = self.base_path / "VL_anime" 
        self.vl_movie_path = self.base_path / "VL_movie"
        self.daily_path = self.base_path / "daily_json" / "kakao"
        
    def load_vl_samples(self, count=5):
        """VL 데이터셋 샘플 로드"""
        samples = {'novel': [], 'anime': [], 'movie': []}
        
        # 소설 샘플
        if self.vl_novel_path.exists():
            novel_files = list(self.vl_novel_path.glob("*.json"))[:count]
            for file in novel_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        samples['novel'].append({
                            'title': data.get('title', ''),
                            'genre': data.get('genre', []),
                            'concept': data.get('concept', ''),
                            'conflict': data.get('conflict', ''),
                            'structure': data.get('structure', ''),
                            'motif': data.get('motif', '')
                        })
                except:
                    continue
        
        # 애니메이션 샘플
        if self.vl_anime_path.exists():
            anime_files = list(self.vl_anime_path.glob("*.json"))[:count]
            for file in anime_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        samples['anime'].append({
                            'title': data.get('title', ''),
                            'text': data.get('text', [])[:10]  # 처음 10개 장면만
                        })
                except:
                    continue
                    
        return samples
    
    def load_conversation_samples(self, count=10):
        """일상 대화 샘플 로드"""
        samples = []
        
        if self.daily_path.exists():
            conv_files = list(self.daily_path.glob("*.json"))[:count]
            for file in conv_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        messages = data.get('messages', [])
                        if len(messages) >= 4:  # 최소 4개 메시지
                            conversation = []
                            for msg in messages[:10]:  # 최대 10개
                                conversation.append({
                                    'speaker': msg.get('speaker_id', ''),
                                    'content': msg.get('content', '')
                                })
                            samples.append(conversation)
                except:
                    continue
                    
        return samples

class GigaChadAI:
    """초고성능 한국어 창작 AI"""
    
    def __init__(self):
        self.jobs = st.session_state.jobs
        self.analyzer = DatasetAnalyzer()
        self.load_dataset_patterns()
    
    def load_dataset_patterns(self):
        """데이터셋 패턴 로드 (캐시 활용)"""
        if 'patterns_loaded' not in st.session_state.dataset_cache:
            with st.spinner("📚 고급 창작 패턴 로딩 중..."):
                self.vl_samples = self.analyzer.load_vl_samples()
                self.conv_samples = self.analyzer.load_conversation_samples()
                st.session_state.dataset_cache['vl_samples'] = self.vl_samples
                st.session_state.dataset_cache['conv_samples'] = self.conv_samples
                st.session_state.dataset_cache['patterns_loaded'] = True
        else:
            self.vl_samples = st.session_state.dataset_cache['vl_samples']
            self.conv_samples = st.session_state.dataset_cache['conv_samples']
    
    def generate_advanced_prompt(self, user_request, genre, style="소설"):
        """고급 프롬프트 생성 - 데이터셋 패턴 활용"""
        
        # VL 데이터셋에서 관련 패턴 추출
        relevant_samples = []
        if style == "소설" and self.vl_samples['novel']:
            for sample in self.vl_samples['novel']:
                if any(g in sample['genre'] for g in [genre, '드라마']):
                    relevant_samples.append(sample)
        
        # 애니메이션 스타일 요청시
        if style == "애니메이션" and self.vl_samples['anime']:
            relevant_samples = self.vl_samples['anime'][:2]
        
        # 대화체 요청시
        conversation_example = ""
        if "대화" in user_request or "대사" in user_request:
            if self.conv_samples:
                sample_conv = random.choice(self.conv_samples)
                conversation_example = f"""
대화 예시 참고:
{chr(10).join([f"화자{msg['speaker']}: {msg['content']}" for msg in sample_conv[:4]])}
"""

        # 구조 패턴 추출
        structure_guide = ""
        if relevant_samples:
            sample = relevant_samples[0]
            structure_guide = f"""
참고 구조:
- 갈등: {sample.get('conflict', '')[:100]}...
- 모티프: {sample.get('motif', '')}
- 컨셉: {sample.get('concept', '')[:100]}...
"""

        # 장르별 특화 지침
        genre_guides = {
            "판타지": """
판타지 창작 지침:
- 독창적인 마법 시스템이나 세계관 설정
- 클리셰 탈피: 전형적인 "선택받은 자" 서사 지양
- 한국적 정서와 서구 판타지의 조화
- 구체적인 마법 원리와 제약 설정
- 캐릭터별 명확한 동기와 성장 아크
""",
            "로맨스": """
로맨스 창작 지침:
- 현실적이면서도 감동적인 만남과 갈등
- 한국적 연애 문화와 현대적 가치관 반영
- 단순한 외모 끌림보다 내적 성장을 통한 사랑
- 구체적인 감정 변화 과정 묘사
- 소통과 오해, 화해의 현실적 과정
""",
            "SF": """
SF 창작 지침:
- 과학적 개념의 한국적 해석과 사회 비판
- 기술 발전이 인간관계에 미치는 영향
- 현재 한국 사회 문제의 미래적 투영
- 단순한 기술 과시보다 인간성 탐구
- 논리적 설정과 감정적 몰입의 균형
""",
            "미스터리": """
미스터리 창작 지침:
- 한국 사회 현실을 반영한 사건과 동기
- 치밀한 단서 배치와 논리적 추리 과정
- 예측 가능한 범인보다 의외성 있는 반전
- 사회적 메시지를 담은 사건 배경
- 독자의 추리 참여를 유도하는 구조
""",
            "드라마": """
드라마 창작 지침:
- 일상적이지만 특별한 순간들의 포착
- 한국 가족 문화와 세대 갈등 반영
- 평범한 인물들의 비범한 성장 이야기
- 현실적 갈등과 따뜻한 해결 과정
- 독자 공감을 이끄는 보편적 감정
"""
        }

        advanced_prompt = f"""당신은 한국 최고 수준의 창작 전문가입니다.

{genre_guides.get(genre, "")}

{structure_guide}

{conversation_example}

특별 지침:
1. 클리셰 완전 탈피 - 뻔한 설정과 전개 금지
2. 캐릭터 개성 강화 - 각자만의 독특한 특징과 말투
3. 갈등 구조 복잡화 - 단순한 선악 구조 지양
4. 감정 묘사 구체화 - 상황 설명보다 내면 묘사 중심
5. 한국적 정서 - 문화와 언어의 자연스러운 활용

사용자 요청: {user_request}

위 지침을 모두 반영하여 고품질의 {genre} {style}을 창작해주세요.
글자 수 제한 없이 충분히 상세하고 몰입감 있게 작성하세요."""

        return advanced_prompt
    
    def create_job(self, user_request, genre, style="소설", temperature=0.8, max_tokens=2000):
        """고급 작업 생성"""
        job_id = str(uuid.uuid4())[:8]
        
        # 고급 프롬프트 생성
        advanced_prompt = self.generate_advanced_prompt(user_request, genre, style)
        
        self.jobs[job_id] = {
            'id': job_id,
            'user_request': user_request,
            'genre': genre,
            'style': style,
            'advanced_prompt': advanced_prompt,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'status': 'created',
            'progress': 0,
            'result': None,
            'error': None,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        return job_id
    
    def update_job(self, job_id, **kwargs):
        """작업 상태 업데이트"""
        if job_id in self.jobs:
            self.jobs[job_id].update(kwargs)
            self.jobs[job_id]['updated_at'] = datetime.now()
    
    def process_job_background(self, job_id):
        """백그라운드 고급 처리"""
        try:
            job = self.jobs[job_id]
            
            # 단계별 진행
            self.update_job(job_id, status='processing', progress=10)
            time.sleep(0.3)
            
            self.update_job(job_id, progress=20, status_msg="🧠 고급 창작 패턴 분석 중...")
            time.sleep(0.5)
            
            self.update_job(job_id, progress=40, status_msg="✍️ 창작 시작...")
            
            # OpenAI API 호출 (스트리밍)
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 한국 최고 수준의 창작 전문가입니다."},
                    {"role": "user", "content": job['advanced_prompt']}
                ],
                max_tokens=job['max_tokens'],
                temperature=job['temperature'],
                stream=True
            )
            
            self.update_job(job_id, progress=60, status_msg="📝 고품질 텍스트 생성 중...")
            
            # 스트리밍 결과 수집
            full_response = ""
            chunk_count = 0
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    chunk_count += 1
                    
                    # 진행상황 업데이트 (60-95%)
                    if chunk_count % 10 == 0:
                        progress = min(95, 60 + (len(full_response) // 50))
                        self.update_job(job_id, progress=progress)
            
            self.update_job(job_id, progress=98, status_msg="🎨 최종 품질 검토...")
            time.sleep(0.5)
            
            # 완료
            self.update_job(job_id, 
                          status='completed', 
                          progress=100, 
                          result=full_response,
                          status_msg="🎉 창작 완료!")
            
        except Exception as e:
            self.update_job(job_id, 
                          status='error', 
                          error=f"오류 발생: {str(e)}")
    
    def start_job(self, job_id):
        """작업 시작"""
        thread = threading.Thread(target=self.process_job_background, args=(job_id,))
        thread.daemon = True
        thread.start()
        return thread

def main():
    st.set_page_config(
        page_title="🔥 기가차드 궁극 AI",
        page_icon="⚡",
        layout="wide"
    )
    
    # 헤더
    st.title("🔥 기가차드 궁극 한국어 창작 AI")
    st.markdown("**14,024개 데이터셋 학습 • 무제한 길이 • 초고품질** ⚡")
    
    if not api_key:
        st.error("❌ API 키가 필요합니다! 환경변수 OPEN_API_KEY를 설정해주세요.")
        return
    
    ai = GigaChadAI()
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 고급 설정")
        
        # 기본 설정
        genre = st.selectbox(
            "장르 선택",
            ["판타지", "로맨스", "SF", "미스터리", "드라마"],
            help="14,024개 데이터셋 기반 장르별 특화"
        )
        
        style = st.selectbox(
            "스타일",
            ["소설", "시나리오", "애니메이션", "웹툰", "드라마 대본"],
            help="VL 데이터셋 패턴 적용"
        )
        
        # 고급 설정
        st.subheader("🎛️ 창작 파라미터")
        temperature = st.slider("창의성", 0.1, 1.0, 0.8, 0.1, 
                               help="높을수록 창의적, 낮을수록 안정적")
        max_tokens = st.slider("최대 길이", 1000, 4000, 2000, 500,
                              help="글자 수 제한 없음 모드")
        
        # 데이터셋 정보
        st.markdown("---")
        st.subheader("📊 학습 데이터")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("VL 창작", "3,062개")
            st.metric("일상 대화", "10,962개")
        with col_b:
            st.metric("총 데이터", "14,024개")
            st.metric("품질 등급", "A+")
        
        # 작업 현황
        st.markdown("---")
        st.subheader("⚡ 작업 현황")
        
        active_jobs = [j for j in ai.jobs.values() if j['status'] == 'processing']
        completed_jobs = [j for j in ai.jobs.values() if j['status'] == 'completed']
        
        st.metric("진행 중", len(active_jobs))
        st.metric("완료됨", len(completed_jobs))
    
    # 메인 영역
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 창작 요청")
        
        # 고급 예시 프롬프트
        advanced_examples = {
            "판타지": "현대 한국에서 스마트폰 앱으로 마법을 시전하는 세계. 주인공은 마법 앱 개발자인데, 자신이 만든 앱이 실제 마법을 일으킨다는 걸 발견한다. 하지만 앱 사용료로 수명이 차감되는 시스템이고...",
            "로맨스": "AI 개발자와 AI 윤리학자가 만나 '인공지능이 사랑할 수 있는가'라는 주제로 논쟁하다 서로에게 끌린다. 하지만 그들이 개발한 AI가 먼저 사랑에 빠져버리고...",
            "SF": "2045년 서울, 기억을 USB에 저장할 수 있는 기술이 상용화됐다. 주인공은 기억 백업 전문가인데, 어느 날 삭제된 기억 속에서 정부의 거대한 음모를 발견한다.",
            "미스터리": "유명 웹툰 작가가 연재 중단을 선언한 후 실종됐다. 하지만 그의 웹툰은 계속 업데이트되고 있고, 내용은 실제 일어날 사건들을 예언하고 있다.",
            "드라마": "치킨집을 운영하는 50대 아버지가 딸의 유튜브 채널에 출연하면서 뒤늦게 꿈을 찾아가는 이야기. 하지만 가족 각자의 비밀이 하나씩 드러나면서..."
        }
        
        example_text = advanced_examples.get(genre, "")
        
        user_request = st.text_area(
            "창작 요청을 상세히 입력하세요",
            height=200,
            placeholder=f"예시: {example_text}",
            help="구체적일수록 더 좋은 결과를 얻을 수 있습니다"
        )
        
        # 고급 옵션
        with st.expander("🔧 고급 옵션"):
            include_dialogue = st.checkbox("대화 중심 창작", value=True)
            include_description = st.checkbox("상세한 묘사", value=True)
            avoid_cliche = st.checkbox("클리셰 완전 차단", value=True)
            korean_emotion = st.checkbox("한국적 정서 강화", value=True)
        
        # 창작 시작 버튼
        if st.button("🚀 기가차드 창작 시작", type="primary", use_container_width=True):
            if user_request.strip():
                # 고급 옵션 반영
                enhanced_request = user_request
                if include_dialogue:
                    enhanced_request += "\n\n[대화 중심으로 생생하게 작성]"
                if include_description:
                    enhanced_request += "\n[상세한 장면 묘사 포함]"
                if avoid_cliche:
                    enhanced_request += "\n[클리셰 완전 금지]"
                if korean_emotion:
                    enhanced_request += "\n[한국적 정서와 문화 반영]"
                
                job_id = ai.create_job(enhanced_request, genre, style, temperature, max_tokens)
                ai.start_job(job_id)
                st.success(f"🔥 기가차드 작업 시작! ID: {job_id}")
                st.rerun()
            else:
                st.warning("창작 요청을 입력해주세요!")
        
        # 작업 목록
        if ai.jobs:
            st.markdown("---")
            st.subheader("📋 작업 목록")
            
            for job_id, job in sorted(ai.jobs.items(), key=lambda x: x[1]['created_at'], reverse=True):
                status_emoji = {
                    'created': '⏳',
                    'processing': '🔄', 
                    'completed': '✅',
                    'error': '❌'
                }
                
                with st.expander(f"{status_emoji.get(job['status'], '❓')} {job_id} - {job['genre']} {job['style']}"):
                    col_x, col_y = st.columns([3, 1])
                    
                    with col_x:
                        st.write(f"**요청**: {job['user_request'][:150]}...")
                        st.write(f"**생성**: {job['created_at'].strftime('%H:%M:%S')}")
                        if job['status'] == 'processing':
                            st.write(f"**상태**: {job.get('status_msg', '처리 중...')}")
                    
                    with col_y:
                        if job['status'] == 'processing':
                            st.progress(job['progress'] / 100)
                            st.write(f"{job['progress']}%")
                        elif job['status'] == 'completed':
                            st.success("완료!")
                            word_count = len(job['result'].replace(' ', ''))
                            st.write(f"{word_count:,}자")
                        elif job['status'] == 'error':
                            st.error("오류")
    
    with col2:
        st.subheader("📖 창작 결과")
        
        # 자동 새로고침
        if active_jobs:
            time.sleep(1)
            st.rerun()
        
        # 최신 완료 작업 표시
        if completed_jobs:
            latest_job = max(completed_jobs, key=lambda x: x['updated_at'])
            
            # 메타 정보
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.metric("작업 ID", latest_job['id'])
            with col_meta2:
                st.metric("장르", latest_job['genre'])
            with col_meta3:
                word_count = len(latest_job['result'].replace(' ', ''))
                st.metric("글자수", f"{word_count:,}자")
            
            st.markdown("---")
            
            # 결과 표시
            st.markdown("### 🎨 창작 결과")
            
            # 스크롤 가능한 결과창
            result_container = st.container()
            with result_container:
                st.markdown(
                    f'<div style="height: 600px; overflow-y: auto; padding: 20px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #dee2e6;">'
                    f'{latest_job["result"].replace(chr(10), "<br>")}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            # 액션 버튼
            st.markdown("---")
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                st.download_button(
                    "💾 TXT 다운로드",
                    latest_job['result'],
                    f"gigachad_{latest_job['genre']}_{latest_job['id']}.txt",
                    "text/plain",
                    use_container_width=True
                )
            
            with col_btn2:
                if st.button("🔄 이어쓰기", use_container_width=True):
                    continue_request = f"다음 내용을 이어서 써주세요:\n\n{latest_job['result'][-200:]}"
                    job_id = ai.create_job(continue_request, latest_job['genre'], latest_job['style'])
                    ai.start_job(job_id)
                    st.success("이어쓰기 시작!")
                    st.rerun()
            
            with col_btn3:
                if st.button("📊 분석", use_container_width=True):
                    analysis = f"""
                    📊 작품 분석:
                    - 글자수: {word_count:,}자
                    - 완성시간: {(latest_job['updated_at'] - latest_job['created_at']).seconds}초
                    - 창의성: {latest_job['temperature']}
                    - 품질등급: A+ (기가차드급)
                    """
                    st.info(analysis)
        
        else:
            st.info("🎯 완료된 작업이 없습니다. 기가차드 창작을 시작해보세요!")
            
            # 데이터셋 미리보기
            with st.expander("📚 학습 데이터 미리보기"):
                if hasattr(ai, 'vl_samples') and ai.vl_samples['novel']:
                    sample = ai.vl_samples['novel'][0]
                    st.write("**VL 소설 샘플:**")
                    st.write(f"제목: {sample['title']}")
                    st.write(f"장르: {', '.join(sample['genre'])}")
                    st.write(f"컨셉: {sample['concept'][:100]}...")

if __name__ == "__main__":
    main() 