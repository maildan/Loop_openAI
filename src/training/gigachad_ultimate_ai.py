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
from typing import TypedDict, Literal, Any, cast

# --- Type Definitions ---

class VLSampleNovel(TypedDict):
    title: str
    genre: list[str]
    concept: str
    conflict: str
    structure: str
    motif: str

class VLSampleAnime(TypedDict):
    title: str
    text: list[str]

class VLSamples(TypedDict):
    novel: list[VLSampleNovel]
    anime: list[VLSampleAnime]
    movie: list[dict[str, object]]  # movie structure is not fully clear

class ConversationMessage(TypedDict):
    speaker: str
    content: str

JobStatus = Literal["created", "running", "completed", "error"]

class Job(TypedDict):
    id: str
    user_request: str
    genre: str
    style: str
    advanced_prompt: str
    temperature: float
    max_tokens: int
    status: JobStatus
    progress: float
    result: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime

class DatasetCache(TypedDict):
    patterns_loaded: bool
    vl_samples: VLSamples
    conv_samples: list[list[ConversationMessage]]


# --- API Key Setup ---

api_key = os.getenv("OPEN_API_KEY") or os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key
    openai_available = True
else:
    openai_available = False


# --- Global State Initialization ---

if "jobs" not in st.session_state:
    st.session_state.jobs = {}
if "dataset_cache" not in st.session_state:
    st.session_state.dataset_cache = {}


class DatasetAnalyzer:
    """데이터셋 분석 및 패턴 추출"""

    def __init__(self) -> None:
        self.base_path: Path = Path("dataset")
        self.vl_novel_path: Path = self.base_path / "VL_novel"
        self.vl_anime_path: Path = self.base_path / "VL_anime"
        self.vl_movie_path: Path = self.base_path / "VL_movie"
        self.daily_path: Path = self.base_path / "daily_json" / "kakao"

    def load_vl_samples(self, count: int = 5) -> VLSamples:
        """VL 데이터셋 샘플 로드"""
        samples: VLSamples = {"novel": [], "anime": [], "movie": []}

        # 소설 샘플
        if self.vl_novel_path.exists():
            novel_files = list(self.vl_novel_path.glob("*.json"))[:count]
            for file in novel_files:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = cast(dict[str, Any], json.load(f))
                        novel_sample: VLSampleNovel = {
                            "title": data.get("title", ""),
                            "genre": data.get("genre", []),
                            "concept": data.get("concept", ""),
                            "conflict": data.get("conflict", ""),
                            "structure": data.get("structure", ""),
                            "motif": data.get("motif", ""),
                        }
                        samples["novel"].append(novel_sample)
                except (json.JSONDecodeError, IOError):
                    continue

        # 애니메이션 샘플
        if self.vl_anime_path.exists():
            anime_files = list(self.vl_anime_path.glob("*.json"))[:count]
            for file in anime_files:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = cast(dict[str, Any], json.load(f))
                        anime_sample: VLSampleAnime = {
                            "title": data.get("title", ""),
                            "text": data.get("text", [])[:10],  # 처음 10개 장면만
                        }
                        samples["anime"].append(anime_sample)
                except (json.JSONDecodeError, IOError):
                    continue
        
        # 영화 샘플 (구조가 불분명하여 일단 그대로 둠)
        if self.vl_movie_path.exists():
            movie_files = list(self.vl_movie_path.glob("*.json"))[:count]
            for file in movie_files:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = cast(dict[str, object], json.load(f))
                        samples["movie"].append(data)
                except (json.JSONDecodeError, IOError):
                    continue

        return samples

    def load_conversation_samples(self, count: int = 10) -> list[list[ConversationMessage]]:
        """일상 대화 샘플 로드"""
        samples: list[list[ConversationMessage]] = []

        if self.daily_path.exists():
            conv_files = list(self.daily_path.glob("*.json"))[:count]
            for file in conv_files:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = cast(dict[str, Any], json.load(f))
                        messages = data.get("messages", [])
                        if len(messages) >= 4:  # 최소 4개 메시지
                            conversation: list[ConversationMessage] = []
                            for msg in messages[:10]:  # 최대 10개
                                conversation.append(
                                    {
                                        "speaker": msg.get("speaker_id", ""),
                                        "content": msg.get("content", ""),
                                    }
                                )
                            samples.append(conversation)
                except (json.JSONDecodeError, IOError):
                    continue

        return samples


class GigaChadAI:
    """초고성능 한국어 창작 AI"""

    def __init__(self) -> None:
        self.jobs: dict[str, Job] = st.session_state.jobs
        self.analyzer: DatasetAnalyzer = DatasetAnalyzer()
        self.vl_samples: VLSamples
        self.conv_samples: list[list[ConversationMessage]]
        self.load_dataset_patterns()

    def load_dataset_patterns(self) -> None:
        """데이터셋 패턴 로드 (캐시 활용)"""
        cache: DatasetCache = st.session_state.dataset_cache
        if "patterns_loaded" not in cache:
            with st.spinner("📚 고급 창작 패턴 로딩 중..."):
                self.vl_samples = self.analyzer.load_vl_samples()
                self.conv_samples = self.analyzer.load_conversation_samples()
                cache["vl_samples"] = self.vl_samples
                cache["conv_samples"] = self.conv_samples
                cache["patterns_loaded"] = True
        else:
            self.vl_samples = cache["vl_samples"]
            self.conv_samples = cache["conv_samples"]

    def generate_advanced_prompt(self, user_request: str, genre: str, style: str = "소설") -> str:
        """고급 프롬프트 생성 - 데이터셋 패턴 활용"""

        # VL 데이터셋에서 관련 패턴 추출
        relevant_samples: list[VLSampleNovel | VLSampleAnime] = []
        if style == "소설" and self.vl_samples["novel"]:
            for sample in self.vl_samples["novel"]:
                if any(g in sample["genre"] for g in [genre, "드라마"]):
                    relevant_samples.append(sample)

        # 애니메이션 스타일 요청시
        elif style == "애니메이션" and self.vl_samples["anime"]:
            relevant_samples.extend(self.vl_samples["anime"][:2])

        # 대화체 요청시
        conversation_example = ""
        if "대화" in user_request or "대사" in user_request:
            if self.conv_samples:
                sample_conv = random.choice(self.conv_samples)
                conversation_example = (
                    "대화 예시 참고:\n"
                    + "\n".join([f"화자{msg['speaker']}: {msg['content']}" for msg in sample_conv[:4]])
                )

        # 구조 패턴 추출
        structure_guide = ""
        if relevant_samples:
            sample = relevant_samples[0]
            if style == "소설":
                novel_sample = cast(VLSampleNovel, sample)
                structure_guide = f"""
참고 구조:
- 갈등: {novel_sample.get('conflict', '')[:100]}...
- 모티프: {novel_sample.get('motif', '')}
- 컨셉: {novel_sample.get('concept', '')[:100]}...
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
""",
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

    def create_job(
        self, user_request: str, genre: str, style: str = "소설", temperature: float = 0.8, max_tokens: int = 2000
    ) -> str:
        """고급 작업 생성"""
        job_id = str(uuid.uuid4())[:8]

        # 고급 프롬프트 생성
        advanced_prompt = self.generate_advanced_prompt(user_request, genre, style)

        job: Job = {
            "id": job_id,
            "user_request": user_request,
            "genre": genre,
            "style": style,
            "advanced_prompt": advanced_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "status": "created",
            "progress": 0.0,
            "result": None,
            "error": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        self.jobs[job_id] = job

        return job_id

    def update_job(self, job_id: str, **kwargs: object) -> None:
        """작업 상태 업데이트"""
        if job_id in self.jobs:
            job_to_update = self.jobs[job_id]
            for key, value in kwargs.items():
                if key in Job.__annotations__:
                    cast(dict[str, object], cast(object, job_to_update))[key] = value
            job_to_update["updated_at"] = datetime.now()

    def process_job_background(self, job_id: str) -> None:
        """백그라운드에서 AI 작업 처리"""
        try:
            job = self.jobs[job_id]
            self.update_job(job_id, status="running")

            # Streaming 응답 처리
            full_response = ""
            if not openai_available:
                raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

            stream = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative writing expert."},
                    {"role": "user", "content": job["advanced_prompt"]},
                ],
                max_tokens=job["max_tokens"],
                temperature=job["temperature"],
                stream=True,
            )

            chunk_count = 0
            for chunk in stream:
                chunk_count += 1
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    # 진행률 업데이트 (예시: 200 청크를 기준으로)
                    progress = min(chunk_count / 200, 0.9)
                    self.update_job(job_id, progress=progress, result=full_response)
                time.sleep(0.02)  # UI 업데이트를 위한 약간의 지연

            self.update_job(job_id, status="completed", progress=1.0, result=full_response)

        except Exception as e:
            error_message = f"작업 처리 중 오류 발생: {e}"
            self.update_job(job_id, status="error", error=error_message, progress=1.0)

    def start_job(self, job_id: str) -> threading.Thread:
        """작업 스레드 시작"""
        thread = threading.Thread(target=self.process_job_background, args=(job_id,))
        thread.daemon = True
        thread.start()
        return thread


def main() -> None:
    """Streamlit UI 메인 함수"""
    _ = st.set_page_config(page_title="기가차드 AI", layout="wide")
    _ = st.title("🔥 기가차드 AI: 초고성능 한국어 스토리 생성기")
    _ = st.caption(f"OpenAI API 사용 가능: {'✅' if openai_available else '❌'}")

    if "ai" not in st.session_state:
        st.session_state.ai = GigaChadAI()
    ai: GigaChadAI = st.session_state.ai

    tab1, tab2, tab3 = st.tabs(["💡 새 스토리 생성", "⏳ 작업 현황", "📚 데이터셋 분석"])

    with tab1:
        _ = st.header("새로운 스토리 아이디어 구상")
        col1, col2 = st.columns(2)

        with col1:
            _ = st.subheader("1. 기본 설정")
            user_request = st.text_area(
                "어떤 이야기를 만들고 싶으신가요?",
                height=150,
                placeholder="예: 우주를 여행하는 고양이의 이야기",
            )
            genre = st.selectbox(
                "장르를 선택하세요.",
                ["판타지", "로맨스", "SF", "미스터리", "드라마"],
            )
            style = st.radio("스타일", ["소설", "애니메이션", "대화체 시나리오"])

        with col2:
            _ = st.subheader("2. 고급 설정")
            temperature = st.slider("창의성 (Temperature)", 0.1, 1.0, 0.8, 0.05)
            max_tokens = st.slider("최대 길이 (Max Tokens)", 500, 4000, 2000, 100)

            if st.button("🚀 기가차드! 스토리 생성 시작!", type="primary", use_container_width=True):
                if user_request and genre and openai_available:
                    with st.spinner("기가차드가 작업을 준비 중입니다..."):
                        job_id = ai.create_job(
                            user_request,
                            genre,
                            style,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        _ = ai.start_job(job_id)
                        _ = st.success(f"작업이 시작되었습니다! (ID: {job_id}) '작업 현황' 탭에서 확인하세요.")
                        _ = st.balloons()
                elif not openai_available:
                    _ = st.error("OpenAI API 키가 설정되지 않았습니다. API 키를 설정해주세요.")
                else:
                    _ = st.warning("이야기 아이디어를 입력해주세요.")

    with tab2:
        _ = st.header("작업 진행 현황")
        if not ai.jobs:
            _ = st.info("아직 생성된 작업이 없습니다. '새 스토리 생성' 탭에서 새 작업을 시작하세요.")
        else:
            # 작업을 최신순으로 정렬
            sorted_jobs: list[Job] = sorted(
                ai.jobs.values(), key=lambda j: j["created_at"], reverse=True
            )

            for job in sorted_jobs:
                with st.expander(
                    f"**{job['id']}**: {job['user_request'][:30]}... ({job['status']})",
                    expanded=job["status"] in ["running", "created"],
                ):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        _ = st.metric("장르", job["genre"])
                    with col2:
                        _ = st.metric("스타일", job["style"])
                    with col3:
                        created_time = job["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                        _ = st.metric("생성 시각", created_time)

                    _ = st.progress(job["progress"], text=f"진행률: {job['progress']:.0%}")

                    if job["status"] == "running":
                        _ = st.info("기가차드가 스토리를 생성 중입니다...")
                    elif job["status"] == "completed":
                        _ = st.success("작업 완료!")
                    elif job["status"] == "error":
                        _ = st.error(f"오류 발생: {job['error']}")

                    if job["result"]:
                        _ = st.subheader("결과물")
                        _ = st.text_area(
                            "생성된 스토리",
                            value=job["result"],
                            height=300,
                            key=f"result_{job['id']}",
                        )
                        result_bytes = job["result"].encode("utf-8")
                        _ = st.download_button(
                            label="결과 다운로드",
                            data=result_bytes,
                            file_name=f"gigachad_story_{job['id']}.txt",
                            mime="text/plain",
                        )
                    if job["status"] == "created":
                        if st.button("작업 재시작", key=f"restart_{job['id']}"):
                            _ = ai.start_job(job['id'])
                            _ = st.rerun()


    with tab3:
        _ = st.header("데이터셋 패턴 분석")
        _ = st.info("기가차드 AI는 아래와 같은 데이터 패턴을 학습하여 더 나은 결과물을 생성합니다.")

        with st.expander("VL (Vess-AI-Verse) 소설 데이터셋 샘플"):
            if ai.vl_samples["novel"]:
                for sample in ai.vl_samples["novel"]:
                    _ = st.write(f"##### {sample['title']}")
                    _ = st.json(sample, expanded=False)
            else:
                _ = st.write("소설 샘플을 찾을 수 없습니다.")

        with st.expander("VL (Vess-AI-Verse) 애니메이션 데이터셋 샘플"):
            if ai.vl_samples["anime"]:
                for sample in ai.vl_samples["anime"]:
                    _ = st.write(f"##### {sample['title']}")
                    _ = st.json(sample, expanded=False)
            else:
                _ = st.write("애니메이션 샘플을 찾을 수 없습니다.")

        with st.expander("일상 대화 데이터셋 샘플"):
            if ai.conv_samples:
                for sample in ai.conv_samples:
                    _ = st.json(sample, expanded=False)
            else:
                _ = st.write("대화 샘플을 찾을 수 없습니다.")


if __name__ == "__main__":
    main()
